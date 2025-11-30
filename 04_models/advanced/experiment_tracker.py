#!/usr/bin/env python3
"""
Track and log all training experiments with consistent metadata.

Usage:
    python 04_models/advanced/experiment_tracker.py \
        --experiment-dir 04_models/advanced/experiments/exp_001 \
        --metrics accuracy=0.87 latency_ms=42 memory_kb=285
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any


def update_experiment_log(experiment_dir: Path, metrics: Dict[str, Any]) -> None:
    """Update experiment log with final metrics."""
    metadata_path = experiment_dir / "experiment_metadata.json"
    
    if not metadata_path.exists():
        raise FileNotFoundError(f"Experiment metadata not found: {metadata_path}")
    
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["results"] = metrics
    metadata["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    metadata["status"] = "completed"
    
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"[tracker] Updated experiment log: {metadata_path}")


def list_experiments(base_dir: Path) -> None:
    """List all experiments with their status."""
    experiments_dir = base_dir / "experiments"
    if not experiments_dir.exists():
        print("[tracker] No experiments directory found")
        return
    
    experiments = sorted(experiments_dir.iterdir())
    print(f"\n[tracker] Found {len(experiments)} experiments:\n")
    
    for exp_dir in experiments:
        metadata_path = exp_dir / "experiment_metadata.json"
        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            status = metadata.get("status", "unknown")
            model_name = metadata.get("config", {}).get("model_name", "unknown")
            print(f"  {exp_dir.name}: {model_name} - {status}")
        else:
            print(f"  {exp_dir.name}: (no metadata)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Track training experiments.")
    parser.add_argument(
        "--experiment-dir",
        type=Path,
        help="Experiment directory to update",
    )
    parser.add_argument(
        "--metrics",
        nargs="+",
        help="Key=value pairs for metrics (e.g., accuracy=0.87 latency_ms=42)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all experiments",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path("04_models/advanced"),
        help="Base directory for experiments",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    
    if args.list:
        list_experiments(args.base_dir)
        return
    
    if not args.experiment_dir:
        raise ValueError("--experiment-dir required (or use --list)")
    
    if not args.metrics:
        raise ValueError("--metrics required")
    
    # Parse metrics
    metrics = {}
    for metric_str in args.metrics:
        if "=" not in metric_str:
            continue
        key, value = metric_str.split("=", 1)
        # Try to convert to number
        try:
            if "." in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            pass
        metrics[key] = value
    
    update_experiment_log(args.experiment_dir, metrics)


if __name__ == "__main__":
    main()

