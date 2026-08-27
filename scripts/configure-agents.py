#!/usr/bin/env python3
"""Safely create/update thin agent adapters without replacing project policy.

The canonical policy remains AGENTS.md. Provider-native agents that already read
AGENTS.md get no duplicate file. Existing provider files are preserved and
backed up before explicit changes.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

FILE_ADAPTERS = {
    "claude": (
        "CLAUDE.md",
        "# Claude Code adapter\n\nRead and obey `AGENTS.md` first. This file contains Claude-specific routing only.\nDo not duplicate or weaken repository policy. Use project skills/hooks only when explicitly configured and task-relevant.\n",
    ),
    "gemini": (
        "GEMINI.md",
        "# Gemini CLI adapter\n\nRead and obey `AGENTS.md` first. Keep this adapter provider-specific and minimal.\nDo not duplicate canonical repository policy.\n",
    ),
    "copilot": (
        ".github/copilot-instructions.md",
        "# GitHub Copilot adapter\n\nFollow the repository contract in `AGENTS.md`. This file only bridges Copilot to the canonical policy.\nDo not restate or weaken the shared rules.\n",
    ),
    "cursor": (
        ".cursor/rules/vibe-start.mdc",
        "---\ndescription: Load the repository's canonical agent contract\nalwaysApply: true\n---\n\nRead and obey `AGENTS.md`. Keep Cursor-specific instructions here only when required by Cursor.\n",
    ),
}

NATIVE_ADAPTERS = {
    "codex": "Codex consumes AGENTS.md and can discover repository .agents/skills; no duplicate policy file required.",
    "kimi": "Kimi consumes AGENTS.md and discovers repository .agents/skills; no duplicate policy file required.",
    "qwen": "Qwen reads AGENTS.md directly. Preserve any existing QWEN.md; use `vibe skills --providers qwen --apply` for skill projection.",
    "hermes": "Hermes remains the orchestrator bridge and should route from AGENTS.md/manifests without adding a competing project policy file.",
    "generic": "Generic agents should read START_HERE.md then AGENTS.md; no provider file is generated.",
}
SUPPORTED = tuple(FILE_ADAPTERS) + tuple(NATIVE_ADAPTERS)


def backup(path: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dst = path.with_name(f"{path.name}.vibe-backup-{stamp}")
    shutil.copy2(path, dst)
    return dst


def write_file_adapter(root: Path, agent: str, apply: bool) -> dict:
    rel, desired = FILE_ADAPTERS[agent]
    path = root / rel
    result = {"agent": agent, "path": rel, "action": "noop"}
    if path.exists():
        current = path.read_text(encoding="utf-8")
        if current == desired:
            return result
        if "AGENTS.md" in current:
            result["action"] = "preserved-existing"
            return result
        result["action"] = "would-backup-and-append" if not apply else "backup-and-append"
        if apply:
            result["backup"] = str(backup(path).relative_to(root))
            suffix = "\n\n<!-- vibe_start canonical-policy bridge -->\nRead and obey `AGENTS.md`; existing instructions in this file remain in force.\n"
            path.write_text(current.rstrip() + suffix, encoding="utf-8")
        return result

    result["action"] = "would-create" if not apply else "created"
    if apply:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(desired, encoding="utf-8")
    return result


def adapter_result(root: Path, agent: str, apply: bool) -> dict:
    if agent in NATIVE_ADAPTERS:
        return {
            "agent": agent,
            "path": "AGENTS.md",
            "action": "native-no-write",
            "note": NATIVE_ADAPTERS[agent],
        }
    return write_file_adapter(root, agent, apply)


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely bootstrap agent-native project adapters")
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--agents", default=",".join(SUPPORTED), help="comma-separated supported agents")
    parser.add_argument("--apply", action="store_true", help="perform writes; default is dry-run")
    args = parser.parse_args()

    root = Path(args.target).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        parser.error(f"target directory does not exist: {root}")

    selected = [x.strip().lower() for x in args.agents.split(",") if x.strip()]
    unknown = sorted(set(selected) - set(SUPPORTED))
    if unknown:
        parser.error("unsupported agent adapter(s): " + ", ".join(unknown))

    canonical = root / "AGENTS.md"
    if not canonical.exists():
        print(json.dumps({"ok": False, "error": "AGENTS.md is required before provider adapters"}, indent=2))
        return 2

    results = [adapter_result(root, agent, args.apply) for agent in selected]
    print(json.dumps({
        "ok": True,
        "mode": "apply" if args.apply else "dry-run",
        "target": str(root),
        "canonicalPolicy": "AGENTS.md",
        "canonicalSkills": ".agents/skills",
        "results": results,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
