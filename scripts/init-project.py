#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def add_if(container: list[str], condition: bool, value: str) -> None:
    if condition and value not in container:
        container.append(value)


def main() -> int:
    project = Path(sys.argv[1] if len(sys.argv) > 1 else ".").expanduser().resolve()
    if not project.exists() or not project.is_dir():
        raise SystemExit(f"target directory does not exist: {project}")

    vibe_dir = project / ".vibe"
    vibe_dir.mkdir(exist_ok=True)
    (project / ".agents/skills").mkdir(parents=True, exist_ok=True)

    files = {p.name for p in project.iterdir()}
    languages: list[str] = []
    frameworks: list[str] = []
    build_systems: list[str] = []
    test_systems: list[str] = []
    infrastructure: list[str] = []

    package = read_json(project / "package.json") if "package.json" in files else {}
    node_deps = {}
    node_deps.update(package.get("dependencies", {}))
    node_deps.update(package.get("devDependencies", {}))
    if package:
        add_if(languages, True, "javascript/typescript")
        manager = package.get("packageManager", "")
        if manager:
            add_if(build_systems, True, manager.split("@", 1)[0])
        elif "pnpm-lock.yaml" in files:
            add_if(build_systems, True, "pnpm")
        elif "yarn.lock" in files:
            add_if(build_systems, True, "yarn")
        else:
            add_if(build_systems, True, "npm")
        for dep, name in [
            ("next", "next.js"), ("react", "react"), ("vue", "vue"),
            ("svelte", "svelte"), ("vite", "vite"), ("@angular/core", "angular"),
            ("react-native", "react-native"), ("expo", "expo"),
            ("tailwindcss", "tailwind"), ("@storybook/react", "storybook"),
        ]:
            add_if(frameworks, dep in node_deps, name)
        add_if(test_systems, "@playwright/test" in node_deps or "playwright" in node_deps, "playwright")
        add_if(test_systems, "vitest" in node_deps, "vitest")
        add_if(test_systems, "jest" in node_deps, "jest")
        add_if(test_systems, "cypress" in node_deps, "cypress")

    pyproject = (project / "pyproject.toml").read_text(errors="ignore").lower() if "pyproject.toml" in files else ""
    requirements = (project / "requirements.txt").read_text(errors="ignore").lower() if "requirements.txt" in files else ""
    pydeps = pyproject + "\n" + requirements
    if pydeps.strip():
        add_if(languages, True, "python")
        for token, name in [
            ("fastapi", "fastapi"), ("django", "django"), ("flask", "flask"),
            ("torch", "pytorch"), ("tensorflow", "tensorflow"), ("transformers", "huggingface-transformers"),
            ("mlflow", "mlflow"), ("langchain", "langchain"), ("llama-index", "llama-index"),
        ]:
            add_if(frameworks, token in pydeps, name)
        add_if(test_systems, "pytest" in pydeps, "pytest")
        add_if(build_systems, "uv" in pydeps or "uv.lock" in files, "uv")
        add_if(build_systems, "poetry" in pydeps or "poetry.lock" in files, "poetry")

    add_if(languages, "Cargo.toml" in files, "rust")
    add_if(build_systems, "Cargo.toml" in files, "cargo")
    add_if(languages, "go.mod" in files, "go")
    add_if(build_systems, "go.mod" in files, "go-modules")
    add_if(languages, "CMakeLists.txt" in files, "c/c++")
    add_if(build_systems, "CMakeLists.txt" in files, "cmake")
    add_if(build_systems, "conanfile.py" in files or "conanfile.txt" in files, "conan")
    add_if(build_systems, "vcpkg.json" in files, "vcpkg")

    add_if(infrastructure, "Dockerfile" in files, "docker")
    add_if(infrastructure, "docker-compose.yml" in files or "compose.yml" in files, "docker-compose")
    add_if(infrastructure, any(project.glob("*.tf")), "terraform")
    add_if(infrastructure, (project / "k8s").is_dir() or (project / "kubernetes").is_dir(), "kubernetes")

    frontend_markers = {"next.js", "react", "vue", "svelte", "angular", "react-native", "expo"}
    ml_markers = {"pytorch", "tensorflow", "huggingface-transformers", "mlflow", "langchain", "llama-index"}
    backend_markers = {"fastapi", "django", "flask"}
    if ml_markers.intersection(frameworks):
        detected_profile = "ai-ml"
    elif frontend_markers.intersection(frameworks):
        detected_profile = "frontend"
    elif "c/c++" in languages:
        detected_profile = "cpp"
    elif backend_markers.intersection(frameworks) or "go" in languages or "rust" in languages:
        detected_profile = "backend"
    else:
        detected_profile = "minimal"

    meta_path = vibe_dir / "project.json"
    existing = read_json(meta_path) if meta_path.exists() else {}
    profile = existing.get("profileOverride") or detected_profile
    meta = {
        **existing,
        "schemaVersion": 2,
        "languages": languages,
        "frameworks": frameworks,
        "buildSystems": build_systems,
        "testSystems": test_systems,
        "infrastructure": infrastructure,
        "detectedProfile": detected_profile,
        "profile": profile,
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    agents = project / "AGENTS.md"
    if not agents.exists():
        agents.write_text(
            "# Project agent context\n\n"
            "Use global `vibe_start`; keep project-specific architecture, commands and conventions here.\n"
            "External skills and provider adapters must not override this file.\n",
            encoding="utf-8",
        )

    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
