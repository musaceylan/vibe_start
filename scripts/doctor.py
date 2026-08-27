#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]).resolve()
errors: list[str] = []
warnings: list[str] = []
parsed: dict[str, dict] = {}

for path in (root / "manifests").glob("*.json"):
    try:
        parsed[path.name] = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.relative_to(root)}: invalid JSON: {exc}")

for extra in (root / "mcp").glob("*.json"):
    try:
        parsed[f"mcp/{extra.name}"] = json.loads(extra.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{extra.relative_to(root)}: invalid JSON: {exc}")

if errors:
    print("FAIL\n" + "\n".join(errors))
    raise SystemExit(1)

allowed_profiles = {"safe", "minimal", "frontend", "backend", "ai-ml", "cpp", "security", "full"}
lock = parsed["repositories.lock.json"]
repos = lock.get("repositories", [])
repo_names = [entry.get("repository") for entry in repos]
if len(repo_names) != len(set(repo_names)):
    errors.append("repositories.lock.json contains duplicate repository entries")
repo_set = set(repo_names)

for entry in repos:
    repository = entry.get("repository", "<missing>")
    status = str(entry.get("status", ""))
    if entry.get("install"):
        commit = entry.get("commit") or ""
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            errors.append("unpinned installable repository: " + repository)
        profiles = entry.get("installProfiles")
        if not profiles:
            errors.append("installable repository missing installProfiles: " + repository)
        else:
            unknown = sorted(set(profiles) - allowed_profiles)
            if unknown:
                errors.append(f"{repository}: unknown installProfiles {unknown}")
        if any(token in status for token in ("candidate", "reference", "benchmark")):
            errors.append(f"{repository}: {status} entries must not auto-install")

capabilities = parsed["capabilities.json"].get("capabilities", {})
bundles = parsed["bundles.json"].get("bundles", {})
for profile, names in bundles.items():
    for name in names:
        if name not in capabilities:
            errors.append(f"bundle {profile} references missing capability {name}")

skills = parsed["skills.json"]
portable = skills.get("portableSkills", [])
portable_names = [skill.get("name") for skill in portable]
if len(portable_names) != len(set(portable_names)):
    errors.append("skills.json contains duplicate portable skill names")
for skill in portable:
    source = skill.get("source")
    if source not in repo_set:
        errors.append(f"portable skill {skill.get('name')} source missing from repositories.lock.json: {source}")
    profiles = set(skill.get("profiles", []))
    unknown = profiles - allowed_profiles - {"mobile"}
    if unknown:
        errors.append(f"portable skill {skill.get('name')} has unknown profiles {sorted(unknown)}")

providers = parsed.get("providers.json", {})
if providers.get("canonicalPolicy") != "AGENTS.md":
    errors.append("providers.json canonicalPolicy must be AGENTS.md")
if providers.get("canonicalSkillRoot") != skills.get("canonicalRoot"):
    errors.append("provider and skill manifests disagree on canonical skill root")

activation = parsed.get("activation.json", {})
for group in activation.get("neverCoActivate", []):
    members = group.get("members", [])
    if len(members) != len(set(members)):
        errors.append(f"activation group {group.get('group')} contains duplicate members")
    if int(group.get("maxActive", 1)) < 1:
        errors.append(f"activation group {group.get('group')} has invalid maxActive")

mcp = parsed.get("mcp/catalog.json", {})
servers = set(mcp.get("servers", {}))
for profile, names in mcp.get("profiles", {}).items():
    missing = sorted(set(names) - servers)
    if missing:
        errors.append(f"MCP profile {profile} references undefined servers {missing}")

# Ensure critical architecture files exist.
for rel in ["AGENTS.md", "START_HERE.md", "manifests/routing.json", "manifests/activation.json", "manifests/providers.json", "scripts/route.py", "scripts/sync-skills.py"]:
    if not (root / rel).exists():
        errors.append("missing required file: " + rel)

secret_pattern = re.compile(r"(?i)(api[_-]?key|password|token|private[_-]?key)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{20,}")
for path in root.rglob("*"):
    if not path.is_file() or ".git/" in str(path) or path.stat().st_size >= 2_000_000:
        continue
    text = path.read_text(errors="ignore")
    if secret_pattern.search(text):
        errors.append("possible secret " + str(path.relative_to(root)))

if not (root / ".github/workflows").exists():
    warnings.append("no GitHub Actions validation workflow found")

if errors:
    print("FAIL")
    for error in errors:
        print("-", error)
    if warnings:
        print("WARN")
        for warning in warnings:
            print("-", warning)
    raise SystemExit(1)

print("OK: manifests consistent; install profiles/pins valid; portable skills/providers aligned; no obvious embedded secrets")
if warnings:
    print("WARN")
    for warning in warnings:
        print("-", warning)
