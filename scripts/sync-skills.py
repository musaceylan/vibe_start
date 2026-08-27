#!/usr/bin/env python3
"""Materialize selected pinned skills into a project's canonical .agents/skills root.

Dry-run by default. Existing files/directories are preserved. Provider views are
symlinks to the canonical root, not copies of third-party skill content.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def source_repo_path(vibe_home: Path, repository: str) -> Path | None:
    owner, name = repository.split("/", 1)
    candidates = [vibe_home / "repos" / f"{owner}__{name}", vibe_home / "repos" / name]
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None


def ensure_link(link: Path, target: Path, apply: bool) -> dict:
    result = {"path": str(link), "target": str(target), "action": "noop"}
    if link.is_symlink():
        try:
            if link.resolve() == target.resolve():
                return result
        except FileNotFoundError:
            pass
        result["action"] = "conflict-existing-symlink"
        return result
    if link.exists():
        result["action"] = "preserved-existing"
        return result
    result["action"] = "would-link" if not apply else "linked"
    if apply:
        link.parent.mkdir(parents=True, exist_ok=True)
        relative = os.path.relpath(target, start=link.parent)
        link.symlink_to(relative, target_is_directory=True)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Project selected vibe_start skills into cross-agent skill roots")
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--profile", default="auto")
    parser.add_argument("--providers", default="auto", help="comma-separated projections: qwen,claude; Codex/Kimi use .agents/skills natively")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    project = Path(args.target).expanduser().resolve()
    if not project.exists() or not project.is_dir():
        parser.error(f"target directory does not exist: {project}")

    vibe_home = Path(os.environ.get("VIBE_HOME", str(Path.home() / ".vibe"))).expanduser().resolve()
    skills_manifest = load_json(repo_root / "manifests/skills.json")

    profile = args.profile
    project_meta = project / ".vibe/project.json"
    if profile == "auto":
        profile = "minimal"
        if project_meta.exists():
            profile = load_json(project_meta).get("profile", "minimal")

    canonical = project / skills_manifest.get("canonicalRoot", ".agents/skills")
    if args.apply:
        canonical.mkdir(parents=True, exist_ok=True)

    selected = []
    for skill in skills_manifest.get("portableSkills", []):
        profiles = skill.get("profiles", [])
        if profile != "full" and profile not in profiles:
            continue
        source_root = source_repo_path(vibe_home, skill["source"])
        if source_root is None:
            selected.append({"name": skill["name"], "action": "source-not-installed", "source": skill["source"]})
            continue
        source = source_root / skill["path"]
        if not source.exists() or not (source / "SKILL.md").exists():
            selected.append({"name": skill["name"], "action": "skill-path-missing", "source": str(source)})
            continue
        result = ensure_link(canonical / skill["name"], source, args.apply)
        result["name"] = skill["name"]
        result["source"] = skill["source"]
        selected.append(result)

    providers: list[str]
    if args.providers == "auto":
        providers = []
        if (project / "QWEN.md").exists() or (project / ".qwen").exists():
            providers.append("qwen")
        if (project / "CLAUDE.md").exists() or (project / ".claude").exists():
            providers.append("claude")
    else:
        providers = [p.strip().lower() for p in args.providers.split(",") if p.strip()]

    projection_roots = {"qwen": project / ".qwen/skills", "claude": project / ".claude/skills"}
    projections = []
    for provider in providers:
        root = projection_roots.get(provider)
        if root is None:
            projections.append({"provider": provider, "action": "native-or-unsupported-no-projection"})
            continue
        if args.apply:
            root.mkdir(parents=True, exist_ok=True)
        for skill in skills_manifest.get("portableSkills", []):
            profiles = skill.get("profiles", [])
            if profile != "full" and profile not in profiles:
                continue
            canonical_skill = canonical / skill["name"]
            if not canonical_skill.exists() and not canonical_skill.is_symlink():
                continue
            result = ensure_link(root / skill["name"], canonical_skill, args.apply)
            result["provider"] = provider
            result["name"] = skill["name"]
            projections.append(result)

    print(json.dumps({
        "ok": True,
        "mode": "apply" if args.apply else "dry-run",
        "profile": profile,
        "target": str(project),
        "canonicalRoot": str(canonical),
        "nativeConsumers": ["codex", "kimi"],
        "skills": selected,
        "projections": projections,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
