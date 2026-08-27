#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def matches(pattern: str, text: str) -> bool:
    try:
        return re.search(pattern, text, re.IGNORECASE) is not None
    except re.error:
        return pattern.lower() in text.lower()


def score_rules(rules: dict, text: str) -> dict[str, int]:
    scores: dict[str, int] = {}
    for name, spec in rules.items():
        weight = int(spec.get("weight", 1))
        hits = sum(1 for pattern in spec.get("patterns", []) if matches(pattern, text))
        scores[name] = hits * weight
    return scores


def unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def main() -> int:
    parser = argparse.ArgumentParser(description="Route a task to the smallest useful vibe_start capability set")
    parser.add_argument("--task", required=True)
    parser.add_argument("--project", default=None, help="optional project root containing .vibe/project.json")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    routing = load_json(root / "manifests/routing.json")
    bundles = load_json(root / "manifests/bundles.json")["bundles"]
    capabilities_manifest = load_json(root / "manifests/capabilities.json")["capabilities"]
    activation = load_json(root / "manifests/activation.json")

    text = args.task.strip().lower()
    project_info: dict = {}
    if args.project:
        project_file = Path(args.project).expanduser().resolve() / ".vibe/project.json"
        if project_file.exists():
            project_info = load_json(project_file)
            text += " " + " ".join(project_info.get("languages", []))
            text += " " + " ".join(project_info.get("frameworks", []))

    profile_scores = score_rules(routing.get("profiles", {}), text)
    profile = max(profile_scores, key=profile_scores.get, default="minimal")
    if profile_scores.get(profile, 0) < int(routing.get("profileThreshold", 2)):
        profile = project_info.get("profile") or "minimal"
    if profile not in bundles:
        profile = "minimal"

    capability_scores = score_rules(routing.get("capabilities", {}), text)
    selected = list(bundles.get(profile, bundles["minimal"]))
    threshold = int(routing.get("capabilityThreshold", 2))
    for name, score in sorted(capability_scores.items(), key=lambda item: (-item[1], item[0])):
        if score >= threshold and name in capabilities_manifest:
            selected.append(name)
    selected = unique(selected)

    specialist_scores = score_rules(routing.get("specialists", {}), text)
    specialist_names = [
        name for name, score in sorted(specialist_scores.items(), key=lambda item: (-item[1], item[0])) if score > 0
    ]

    # Enforce default non-coactivation. Comparative/benchmark wording may keep both.
    comparative = any(word in text for word in ("compare", "comparative", "benchmark against", "a/b"))
    if not comparative:
        for group in activation.get("neverCoActivate", []):
            members = [m for m in group.get("members", []) if m in specialist_names]
            limit = int(group.get("maxActive", 1))
            if len(members) > limit:
                keep = sorted(members, key=lambda n: (-specialist_scores.get(n, 0), specialist_names.index(n)))[:limit]
                specialist_names = [n for n in specialist_names if n not in members or n in keep]

    specialist_specs = routing.get("specialists", {})
    specialists = []
    activation_modes = activation.get("activation", {})
    for name in specialist_names:
        mode = specialist_specs.get(name, {}).get("mode") or activation_modes.get(name, {}).get("mode") or "task-scoped"
        specialists.append({"name": name, "mode": mode, "score": specialist_scores[name]})

    verification: list[str] = []
    for capability in selected:
        verification.extend(capabilities_manifest.get(capability, {}).get("verify", []))
    verification = unique(verification)

    risk = routing.get("risk", {}).get("default", "low")
    for level in ("high", "medium"):
        if any(matches(pattern, text) for pattern in routing.get("risk", {}).get(level, [])):
            risk = level
            break

    complexity = len(selected) + len(specialists)
    budget_name = "low" if complexity <= 4 else "medium" if complexity <= 8 else "high"
    budget = routing.get("contextBudget", {}).get(budget_name, {})

    result = {
        "profile": profile,
        "capabilities": selected,
        "specialists": specialists,
        "verification": verification,
        "risk": risk,
        "contextBudget": {"name": budget_name, **budget},
        "scores": {
            "profiles": {k: v for k, v in profile_scores.items() if v},
            "capabilities": {k: v for k, v in capability_scores.items() if v},
        },
        "instruction": "load only selected capabilities and specialists; escalate context gradually; verification is independent from creation",
    }
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
