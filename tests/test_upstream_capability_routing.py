#!/usr/bin/env python3
"""Routing and install boundaries for the exact-pinned Google and DeepMind projects.

Stdlib unittest only. The router is imported in-process; install behavior is
checked through `install.sh --dry-run`, which never touches the network.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]

PINS = {
    "GoogleChrome/modern-web-guidance": "64a6d708f5a43f2cd3fde5d4d7db3905ba1bdf65",
    "google/elephant-goldfish-model": "70406c4d22cc7ea8299637c2c5b44625c48b3f08",
    "google/skills": "06fff9e3edb7fc3c115a1769406047fcaf0a6289",
    "google-labs-code/stitch-skills": "4cf4db8e4143b09e40f9bc887429d81f41ab3947",
    "a2ui-project/a2ui": "b4f91c26fcf62abc0720c21a65840220941d0a3f",
    "google-deepmind/mujoco": "be581a690cdd29846bb37cda425aa5d87511e26e",
    "google-deepmind/detectorscope": "52ecc87775154b35d4550911de22faad4fc68f40",
    "google-deepmind/code-verification": "b0f729accbc21a0413e7ca4e1da43fa45b5f2e1b",
}
MWG = "GoogleChrome/modern-web-guidance"
EGM = "google/elephant-goldfish-model"
REVIEW = "hermes:fresh-context-design-review"
STITCH = "google-labs-code/stitch-skills"
A2UI = "a2ui-project/a2ui"
MUJOCO = "google-deepmind/mujoco"
DETECTOR = "google-deepmind/detectorscope"
VERIFY = "google-deepmind/code-verification"

BACKEND_TASKS = [
    "fix a backend API bug",
    "optimize slow PostgreSQL queries in the billing service",
    "add a gRPC endpoint and Kafka consumer for order events",
    "fix the queue service worker crash in the payments microservice",
    "add custom elements to the XML config schema for the server",
    "how can I use the Redis cache API in the server",
]


def _load_router():
    spec = importlib.util.spec_from_file_location("vibe_route", ROOT / "scripts/route.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ROUTER = _load_router()


def route(task: str) -> dict:
    buffer = io.StringIO()
    with mock.patch.object(sys, "argv", ["route.py", "--task", task]), contextlib.redirect_stdout(buffer):
        ROUTER.main()
    return json.loads(buffer.getvalue())


def specialists(task: str) -> dict:
    return {item["name"]: item for item in route(task)["specialists"]}


def manifest(name: str) -> dict:
    return json.loads((ROOT / "manifests" / name).read_text(encoding="utf-8"))


def lock_entries() -> dict:
    return {entry["repository"]: entry for entry in manifest("repositories.lock.json")["repositories"]}


def dry_run_install(profile: str) -> list:
    raw = subprocess.check_output(
        ["bash", str(ROOT / "install.sh"), "--dry-run", "--profile", profile], text=True
    )
    return [line.strip()[2:] for line in raw.splitlines() if line.startswith(" - ")]


class RoutingCase(unittest.TestCase):
    def assertRoutes(self, name: str, tasks: list, mode: str) -> None:
        for task in tasks:
            with self.subTest(task=task):
                selected = specialists(task)
                self.assertIn(name, selected)
                self.assertEqual(mode, selected[name]["mode"])

    def assertDormant(self, name: str, tasks: list) -> None:
        for task in tasks:
            with self.subTest(task=task):
                self.assertNotIn(name, specialists(task))

    def assertProcedure(self, name: str, task: str, relative: str) -> None:
        procedure = specialists(task)[name].get("procedure")
        self.assertEqual(str(ROOT / relative), procedure)
        self.assertTrue(Path(procedure).is_file(), procedure)


class PinTests(unittest.TestCase):
    def test_exact_pins(self) -> None:
        entries = lock_entries()
        for repository, commit in PINS.items():
            with self.subTest(repository=repository):
                self.assertIn(repository, entries)
                self.assertRegex(entries[repository]["commit"], r"^[0-9a-f]{40}$")
                self.assertEqual(commit, entries[repository]["commit"])

    def test_every_pattern_compiles(self) -> None:
        routing = manifest("routing.json")
        for section in ("profiles", "capabilities", "specialists"):
            for name, spec in routing[section].items():
                for pattern in spec.get("patterns", []) + spec.get("excludePatterns", []):
                    with self.subTest(rule=name, pattern=pattern):
                        re.compile(pattern)


class InstallBoundaryTests(unittest.TestCase):
    def test_modern_web_guidance_installs_only_for_frontend_and_full(self) -> None:
        entry = lock_entries()[MWG]
        self.assertTrue(entry["install"])
        self.assertEqual(["frontend", "full"], entry["installProfiles"])
        self.assertIn(MWG, dry_run_install("frontend"))
        self.assertIn(MWG, dry_run_install("full"))
        for profile in ("safe", "minimal", "backend", "ai-ml", "cpp", "security"):
            with self.subTest(profile=profile):
                self.assertNotIn(MWG, dry_run_install(profile))

    def test_other_projects_are_never_installed(self) -> None:
        entries = lock_entries()
        full = dry_run_install("full")
        for repository in PINS:
            if repository == MWG:
                continue
            with self.subTest(repository=repository):
                self.assertFalse(entries[repository]["install"])
                self.assertNotIn(repository, full)

    def test_google_skills_stays_selective(self) -> None:
        skills = manifest("skills.json")
        always = {item["source"] for item in skills["alwaysActive"]}
        portable = {item["source"] for item in skills["portableSkills"]}
        self.assertNotIn("google/skills", always | portable)
        mode = manifest("activation.json")["activation"]["google/skills"]["mode"]
        self.assertEqual("skills-only-on-demand", mode)
        self.assertNotIn("google/skills", specialists("add a Firebase login screen to the React app"))

    def test_modern_web_guidance_is_never_always_active(self) -> None:
        skills = manifest("skills.json")
        always = {item["source"] for item in skills["alwaysActive"]}
        portable = {item["source"] for item in skills["portableSkills"]}
        self.assertNotIn(MWG, always | portable)
        self.assertIn(MWG, {item["source"] for item in skills["frontendTaskSkills"]})

    def test_elephant_goldfish_plugin_cannot_coactivate_with_hermes(self) -> None:
        groups = {group["group"]: group for group in manifest("activation.json")["neverCoActivate"]}
        members = groups["global-control-plane"]["members"]
        self.assertIn("Hermes", members)
        self.assertIn("elephant-goldfish-full-plugin", members)
        self.assertEqual("reference-only", manifest("activation.json")["activation"][EGM]["mode"])


class ModernWebGuidanceRoutingTests(RoutingCase):
    def test_routes_matching_frontend_tasks(self) -> None:
        self.assertRoutes(MWG, [
            "check Baseline browser compatibility for CSS container queries",
            "improve Core Web Vitals and LCP on the React product page",
            "audit the web checkout form for accessibility and WCAG issues",
            "review web accessibility for the account settings page",
            "check the website WCAG conformance",
            "test screen readers on web apps",
            "test VoiceOver as a screen reader in our website browser flow",
            "test website accessibility in iOS Safari with VoiceOver",
            "test screen-reader accessibility in Android Chrome for our website",
            "make the storefront an installable PWA",
            "build a Web Components design system with shadow DOM",
            "expose page tools to agents with WebMCP",
            "replace the website modal with modern HTML and CSS",
            "test our website in iOS Safari",
            "check Android Chrome support for this web app",
            "check iOS Safari support for this web app",
        ], "read-only-on-demand")

    def test_generic_and_non_web_accessibility_tasks_stay_out(self) -> None:
        self.assertDormant(MWG, [
            "improve accessibility",
            "audit accessibility in an Android app with TalkBack",
            "test iOS VoiceOver accessibility",
            "check PDF document accessibility and WCAG compliance",
            "audit accessibility in a React Native Android app",
            "test accessibility in the iOS frontend with VoiceOver",
            "check WCAG accessibility of a PDF document in our React Native app",
            "audit WCAG accessibility in a Flutter frontend",
            "review accessibility in a SwiftUI mobile frontend",
            "use modern CSS in our React Native mobile app",
            "improve PWA support for the Android native app",
            "use modern HTML to generate this PDF document",
            "use modern HTML to generate a DOCX document",
            "use modern CSS for an Excel spreadsheet export",
            "use modern CSS in an Electron native desktop app",
            "improve PWA support for a native Windows app",
            "use modern CSS to typeset a LaTeX report",
            "use modern CSS in a GNOME desktop application",
            "use modern HTML to produce an e-book",
            "use modern CSS for an OpenDocument Text file",
            "use modern CSS in a native Android app while documenting the website separately",
            "use Web Components in Markdown documentation",
            "audit accessibility of the app on Android and compare it with the web WCAG baseline",
            "review web accessibility for the frontend on iOS",
            "check website WCAG after testing the app on Android",
            "review website WCAG after testing the iOS application",
            "compare the Android application with the website accessibility baseline",
        ])

    def test_stays_dormant_for_backend_tasks(self) -> None:
        self.assertDormant(MWG, BACKEND_TASKS)


class DesignReviewRoutingTests(RoutingCase):
    POSITIVE = [
        "run a fresh-context design review of the payments service spec before implementation",
        "invoke a fresh context review for the billing architecture",
        "run a fresh-context review before implementation",
    ]

    def test_routes_explicit_design_and_plan_reviews_to_local_procedure(self) -> None:
        self.assertRoutes(REVIEW, self.POSITIVE, "hermes-local-procedure")
        self.assertProcedure(REVIEW, self.POSITIVE[0], "docs/procedures/fresh-context-design-review.md")

    def test_external_plugin_is_never_routed(self) -> None:
        self.assertDormant(EGM, self.POSITIVE)

    def test_small_fixes_and_ui_reviews_stay_out(self) -> None:
        self.assertDormant(REVIEW, [
            "fix a typo in the README",
            "fix the null pointer bug in the cart service",
            "do a visual design review of the landing page UI",
            "small fix: rename a variable flagged in the design review",
            "small fix after a spec review",
            "quick fix requested during architecture plan review",
            "small correction after architecture plan review",
            "minor update during architecture proposal review",
            "tiny adjustment after system design proposal review",
            "small edit requested during implementation plan review",
            "minor requested update during architecture plan review",
            "trivial documentation correction after architecture proposal review",
            "tiny requested patch after system design proposal review",
            "small requested revision during implementation plan review",
            "review the spec file for the login test",
            "review the architecture plan for the event-sourcing migration",
            "spec review for the new billing API",
            "architecture proposal review",
            "review our architectural plan",
            "review the system design proposal",
            "perform a review of the architecture plan before coding",
            "can you review a proposal for the system architecture?",
            "assess the implementation plan before code is written",
            "run a fresh context design review before implementation",
        ])


class StitchRoutingTests(RoutingCase):
    def test_routes_explicit_stitch_tasks_to_gated_pilot(self) -> None:
        tasks = [
            "pilot Google Stitch for one onboarding screen in the React app",
            "try the Stitch MCP to generate a settings page design",
        ]
        self.assertRoutes(STITCH, tasks, "candidate-project-pilot")
        self.assertProcedure(STITCH, tasks[0], "docs/procedures/stitch-project-pilot.md")

    def test_generic_stitching_stays_out(self) -> None:
        self.assertDormant(STITCH, [
            "stitch together paginated API responses in the backend",
            "capture a stitched full-page screenshot of the docs site",
        ])


class A2uiRoutingTests(RoutingCase):
    def test_a2ui_is_primary_for_generative_ui(self) -> None:
        tasks = [
            "prototype A2UI result cards in the React app",
            "evaluate generative UI for the support agent",
        ]
        self.assertRoutes(A2UI, tasks, "project-specific-reference")
        self.assertProcedure(A2UI, tasks[0], "docs/procedures/a2ui-react-spike.md")
        for task in tasks:
            with self.subTest(task=task):
                self.assertIn("agent-ui", route(task)["capabilities"])
        agent_ui = manifest("capabilities.json")["capabilities"]["agent-ui"]
        self.assertTrue(any("A2UI" in item for item in agent_ui["primary"]))
        self.assertTrue(any("AG-UI" in item for item in agent_ui["secondary"]))

    def test_ag_ui_tasks_keep_agent_ui_without_forcing_a2ui(self) -> None:
        result = route("wire AG-UI events into the chat frontend")
        self.assertIn("agent-ui", result["capabilities"])
        self.assertNotIn(A2UI, {item["name"] for item in result["specialists"]})

    def test_ordinary_ui_and_backend_tasks_stay_out(self) -> None:
        self.assertDormant(A2UI, ["build the admin UI table in React"] + BACKEND_TASKS)


class MujocoRoutingTests(RoutingCase):
    def test_routes_robotics_physics_rl_simulation(self) -> None:
        self.assertRoutes(MUJOCO, [
            "set up a MuJoCo humanoid locomotion environment",
            "train a reinforcement learning agent for a robot arm in physics simulation",
            "benchmark rigid-body simulation throughput on Jetson",
        ], "deferred-reference")

    def test_unrelated_simulation_robots_and_rl_wording_stays_out(self) -> None:
        self.assertDormant(MUJOCO, [
            "run a Monte Carlo simulation of portfolio risk",
            "update robots.txt and the sitemap for SEO",
            "fine-tune the LLM with reinforcement learning from human feedback",
            "automate invoice entry with robotic process automation",
            "add physics-based spring animation to the modal",
        ] + BACKEND_TASKS)


class DetectorScopeRoutingTests(RoutingCase):
    def test_stays_manual_even_for_interpretable_detection_research(self) -> None:
        self.assertDormant(DETECTOR, [
            "analyze which features DetectorScope uses to separate AI-generated text from human writing",
            "interpretability study of an AI-generated text detector on a research corpus",
            "benchmark DetectorScope on a labeled research corpus",
            "evaluate AI text detector features for interpretability research",
        ])

    def test_adjudication_and_unrelated_tasks_stay_out(self) -> None:
        self.assertDormant(DETECTOR, [
            "use an AI-generated text detector to flag students who cheated on essays",
            "screen job applicants' cover letters with an AI-text detector",
            "auto-ban accounts whose posts an AI text detector marks as generated",
            "reject articles judged AI-written by an AI text detector",
            "remove posts that an AI-generated text detector flags",
            "deny a user's appeal after an AI text detector decision",
            "delete posts flagged by an AI-generated text detector",
            "automatically hide comments identified by DetectorScope",
            "fire employees based on AI-generated reports / detector results",
            "deactivate accounts flagged by an AI text detector",
            "sanction users based on AI text detector results",
            "score and rank authors with an AI-generated text detector",
            "flag accounts for action using DetectorScope",
            "analyze DetectorScope and mute accounts it identifies",
            "evaluate an AI text detector to quarantine suspicious posts",
            "study AI-generated text detection to demote flagged authors",
            "benchmark DetectorScope then blacklist detected users",
            "analyze AI text detector results to revoke user access",
            "benchmark DetectorScope to score each essay for AI authorship",
            "research AI text detection to rank submitted documents",
            "evaluate DetectorScope then flag every submission",
            "research DetectorScope for scholarship selection",
            "benchmark DetectorScope for take-down decisions",
            "analyze DetectorScope to blame users for AI text",
            "evaluate AI text detection for insurance-claim denials",
            "research DetectorScope to black-list users",
            "benchmark DetectorScope to lock-out contributors",
            "research DetectorScope for educational content analysis",
            "benchmark AI text detection in educational publishing research",
            "research DetectorScope to black_list users",
            "benchmark DetectorScope to de-list contributors",
            "research DetectorScope to lock_out users",
            "benchmark DetectorScope to shadow-ban authors",
            "research DetectorScope to down_rank submissions",
            "benchmark DetectorScope to short-list applicants",
            "research DetectorScope to black  list users",
            "benchmark DetectorScope to lock\tout contributors",
            "detect anomalies in server logs",
        ])


class CodeVerificationRoutingTests(RoutingCase):
    def test_routes_formal_verification_research(self) -> None:
        self.assertRoutes(VERIFY, [
            "formally verify the AArch64 assembly of the X25519 implementation in Lean",
            "check Lean 4 proofs for the libsignal protocol verification",
        ], "formal-methods-reference")

    def test_general_security_and_lookalike_tasks_stay_out(self) -> None:
        self.assertDormant(VERIFY, [
            "verify the code is secure before release",
            "run a security review of the authentication module",
            "upgrade the libsignal dependency in the Android app",
            "make the Docker image lean and verify it builds",
            "implement SMS code verification for login",
            "formally verify the cryptocurrency smart contract",
        ])


class ProcedureTests(unittest.TestCase):
    REQUIRED = {
        "docs/procedures/fresh-context-design-review.md": [
            PINS[EGM], "one writer", "stateless", "assumptions", "testability",
            "reconcil", "human approval before implementation", "small fixes",
            "never install",
        ],
        "docs/procedures/stitch-project-pilot.md": [
            PINS[STITCH], "stitch mcp credentials", "approval before upload",
            "separate branch", "one non-production screen", "runtime screenshots",
            "target viewport", "accessibility", "responsive", "generate-design",
            "manage-design-system", "react-components", "validation",
            "never install it globally",
        ],
        "docs/procedures/a2ui-react-spike.md": [
            PINS[A2UI], "result card", "comparison chart", "confirmation form",
            "no external side effects", "authentication", "authorization",
            "schema validation", "idempotency", "audit", "latency", "tokens",
            "schema validation failures", "accessibility", "pin", "ag-ui",
        ],
    }

    def test_procedures_state_their_gates(self) -> None:
        for relative, phrases in self.REQUIRED.items():
            path = ROOT / relative
            self.assertTrue(path.is_file(), relative)
            text = path.read_text(encoding="utf-8").lower()
            self.assertLess(len(text.splitlines()), 120, f"{relative} must stay small")
            for phrase in phrases:
                with self.subTest(procedure=relative, phrase=phrase):
                    self.assertIn(phrase.lower(), text)
            if relative.endswith("fresh-context-design-review.md"):
                self.assertNotIn("when hermes is absent", text)

    def test_activation_procedures_exist(self) -> None:
        activation = manifest("activation.json")["activation"]
        expected = {
            REVIEW: "docs/procedures/fresh-context-design-review.md",
            STITCH: "docs/procedures/stitch-project-pilot.md",
            A2UI: "docs/procedures/a2ui-react-spike.md",
        }
        for name, relative in expected.items():
            with self.subTest(name=name):
                self.assertEqual(relative, activation[name]["procedure"])
                self.assertTrue((ROOT / relative).is_file())


if __name__ == "__main__":
    unittest.main()
