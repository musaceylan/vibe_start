#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path


def mean(values: list[float]) -> float | None:
    return round(statistics.fmean(values), 3) if values else None


def run_router_benchmark(root: Path) -> dict:
    cases = json.loads((root / "tests/router-fixtures.json").read_text(encoding="utf-8"))["cases"]
    profile_ok = 0
    capability_expected = 0
    capability_found = 0
    specialist_expected = 0
    specialist_found = 0
    selected_capabilities = []
    selected_specialists = []
    timings = []

    for case in cases:
        start = time.perf_counter()
        raw = subprocess.check_output([
            sys.executable, str(root / "scripts/route.py"), "--task", case["task"]
        ], text=True)
        timings.append((time.perf_counter() - start) * 1000)
        result = json.loads(raw)
        profile_ok += int(result["profile"] == case["profile"])
        actual_caps = set(result.get("capabilities", []))
        expected_caps = set(case.get("capabilities", []))
        capability_expected += len(expected_caps)
        capability_found += len(expected_caps & actual_caps)
        actual_specs = {x["name"] for x in result.get("specialists", [])}
        expected_specs = set(case.get("specialists", []))
        specialist_expected += len(expected_specs)
        specialist_found += len(expected_specs & actual_specs)
        selected_capabilities.append(len(actual_caps))
        selected_specialists.append(len(actual_specs))

    return {
        "cases": len(cases),
        "profileAccuracy": round(profile_ok / len(cases), 4) if cases else 1.0,
        "capabilityRecall": round(capability_found / capability_expected, 4) if capability_expected else 1.0,
        "specialistRecall": round(specialist_found / specialist_expected, 4) if specialist_expected else 1.0,
        "avgSelectedCapabilities": mean([float(x) for x in selected_capabilities]),
        "avgSelectedSpecialists": mean([float(x) for x in selected_specialists]),
        "avgRouteLatencyMs": mean(timings),
    }


def load_results(path: Path) -> list[dict]:
    records = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}")
        if item.get("mode") not in {"plain", "vibe"} or "taskId" not in item or "success" not in item:
            raise SystemExit(f"{path}:{line_no}: mode/taskId/success are required")
        records.append(item)
    return records


def aggregate(records: list[dict]) -> dict:
    by_mode: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        by_mode[record["mode"]].append(record)
    metrics = ["tokens", "contextLoadedTokens", "toolCalls", "duplicateReads", "latencyMs", "defects", "rework"]
    output = {}
    for mode, rows in sorted(by_mode.items()):
        result = {
            "runs": len(rows),
            "successRate": round(sum(bool(row["success"]) for row in rows) / len(rows), 4),
            "testsPassRate": round(sum(bool(row.get("testsPassed")) for row in rows if "testsPassed" in row) / max(1, sum("testsPassed" in row for row in rows)), 4),
        }
        for metric in metrics:
            values = [float(row[metric]) for row in rows if metric in row]
            if values:
                result[f"avg{metric[0].upper() + metric[1:]}"] = mean(values)
        output[mode] = result
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark vibe_start routing and optional plain-vs-vibe agent runs")
    parser.add_argument("--results", help="optional JSONL results following benchmarks/result-schema.json")
    parser.add_argument("--require-router-accuracy", type=float, default=1.0)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    report = {"router": run_router_benchmark(root)}
    if args.results:
        report["agentRuns"] = aggregate(load_results(Path(args.results).expanduser().resolve()))
    print(json.dumps(report, indent=2))

    router = report["router"]
    required = args.require_router_accuracy
    if min(router["profileAccuracy"], router["capabilityRecall"], router["specialistRecall"]) < required:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
