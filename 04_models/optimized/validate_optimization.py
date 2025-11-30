#!/usr/bin/env python3
"""
Validate optimized models meet deployment targets.

Usage:
    python 04_models/optimized/validate_optimization.py \
        --benchmark 04_models/optimized/benchmarks/v2.0_int8_benchmark.json \
        --targets 04_models/optimized/configs/simulation_targets.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any


def load_benchmark(benchmark_path: Path) -> Dict[str, Any]:
    """Load benchmark results."""
    return json.loads(benchmark_path.read_text(encoding="utf-8"))


def load_targets(targets_path: Path) -> Dict[str, Any]:
    """Load target requirements."""
    data = json.loads(targets_path.read_text(encoding="utf-8"))
    return data.get("targets", {})


def validate_benchmark(benchmark: Dict[str, Any], targets: Dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate benchmark against targets."""
    metrics = benchmark.get("metrics", {})
    issues = []
    all_passed = True
    
    # Check latency
    latency = metrics.get("latency_ms") or metrics.get("inference_time_ms")
    target_latency = targets.get("latency_ms", 50.0)
    if latency is not None:
        if latency >= target_latency:
            issues.append(f"Latency {latency}ms >= target {target_latency}ms")
            all_passed = False
    else:
        issues.append("Latency metric missing")
        all_passed = False
    
    # Check model size
    flash = metrics.get("flash_kb") or metrics.get("size_kb")
    ram = metrics.get("ram_kb") or metrics.get("peak_ram_kb", 0)
    total_memory = (flash or 0) + ram
    target_size = targets.get("model_size_kb", 300.0)
    
    if total_memory > 0:
        if total_memory >= target_size:
            issues.append(f"Total memory {total_memory:.2f}KB >= target {target_size}KB")
            all_passed = False
    else:
        issues.append("Memory metrics missing")
        all_passed = False
    
    return all_passed, issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate optimization targets.")
    parser.add_argument(
        "--benchmark",
        type=Path,
        required=True,
        help="Benchmark JSON file",
    )
    parser.add_argument(
        "--targets",
        type=Path,
        default=Path("04_models/optimized/configs/simulation_targets.json"),
        help="Targets JSON file",
    )
    parser.add_argument(
        "--exit-on-fail",
        action="store_true",
        help="Exit with error code if validation fails",
    )
    
    args = parser.parse_args()
    
    benchmark = load_benchmark(args.benchmark)
    targets = load_targets(args.targets)
    
    print(f"[validation] Validating {args.benchmark.name}")
    print(f"[validation] Targets: latency < {targets.get('latency_ms', 50)}ms, size < {targets.get('model_size_kb', 300)}KB")
    
    passed, issues = validate_benchmark(benchmark, targets)
    
    if passed:
        print("[validation] ✅ All targets met!")
        sys.exit(0)
    else:
        print("[validation] ❌ Validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        if args.exit_on_fail:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()

