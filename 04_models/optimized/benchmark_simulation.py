#!/usr/bin/env python3
"""
Benchmark optimized models using Edge Impulse simulation.

Usage:
    python 04_models/optimized/benchmark_simulation.py \
        --model 04_models/optimized/quantized/v2.0_int8/model.eim \
        --target-mcu cortex-m4f \
        --output 04_models/optimized/benchmarks/v2.0_int8_benchmark.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List


def run_edge_impulse_simulation(
    model_path: Path,
    target_mcu: str,
    frequency_mhz: int = 80
) -> Dict[str, Any]:
    """Run Edge Impulse simulation benchmark."""
    print(f"[benchmark] Running simulation for {model_path.name}")
    print(f"[benchmark] Target MCU: {target_mcu} @ {frequency_mhz}MHz")
    
    # Edge Impulse simulation command
    # This is a placeholder - actual command requires EI CLI and API key
    cmd = [
        "edge-impulse-cli",
        "deployment",
        "benchmark",
        "--model", str(model_path),
        "--target", target_mcu,
        "--frequency", str(frequency_mhz),
    ]
    
    # For now, create a template result
    # In practice, this would run the actual command and parse output
    result = {
        "model_path": str(model_path),
        "target_mcu": target_mcu,
        "frequency_mhz": frequency_mhz,
        "simulated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "metrics": {
            "latency_ms": None,  # To be filled by actual simulation
            "flash_kb": None,
            "ram_kb": None,
            "peak_ram_kb": None,
            "inference_time_ms": None,
            "cycles": None,
        },
        "status": "pending_simulation",
        "command": " ".join(cmd),
    }
    
    return result


def calculate_model_size(model_path: Path) -> Dict[str, float]:
    """Calculate model file size."""
    if not model_path.exists():
        return {"size_kb": 0.0, "size_bytes": 0}
    
    size_bytes = model_path.stat().st_size
    return {
        "size_kb": size_bytes / 1024.0,
        "size_bytes": size_bytes,
    }


def validate_targets(benchmark: Dict[str, Any], targets: Dict[str, float]) -> Dict[str, bool]:
    """Validate benchmark results against targets."""
    metrics = benchmark.get("metrics", {})
    validation = {}
    
    # Check latency
    latency = metrics.get("latency_ms") or metrics.get("inference_time_ms")
    if latency is not None:
        validation["latency_ok"] = latency < targets.get("latency_ms", 50.0)
    else:
        validation["latency_ok"] = None
    
    # Check model size
    size_kb = metrics.get("flash_kb") or metrics.get("size_kb")
    if size_kb is not None:
        validation["size_ok"] = size_kb < targets.get("model_size_kb", 300.0)
    else:
        validation["size_ok"] = None
    
    # Check total memory
    flash = metrics.get("flash_kb", 0)
    ram = metrics.get("ram_kb", 0) or metrics.get("peak_ram_kb", 0)
    if flash and ram:
        total_memory = flash + ram
        validation["memory_ok"] = total_memory < targets.get("model_size_kb", 300.0)
    else:
        validation["memory_ok"] = None
    
    return validation


def generate_benchmark_report(
    benchmark: Dict[str, Any],
    validation: Dict[str, bool],
    output_path: Path
) -> None:
    """Generate markdown benchmark report."""
    metrics = benchmark.get("metrics", {})
    
    report = f"""# Model Simulation Benchmark Report

**Model**: `{benchmark['model_path']}`
**Target MCU**: {benchmark['target_mcu']} @ {benchmark['frequency_mhz']}MHz
**Simulated**: {benchmark['simulated_at']}

## Performance Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Latency | {metrics.get('latency_ms') or metrics.get('inference_time_ms', 'N/A')} ms | < 50 ms | {"✅" if validation.get('latency_ok') else "❌" if validation.get('latency_ok') is False else "⏳"} |
| Flash Size | {metrics.get('flash_kb', 'N/A')} KB | < 300 KB | {"✅" if validation.get('size_ok') else "❌" if validation.get('size_ok') is False else "⏳"} |
| RAM Usage | {metrics.get('ram_kb') or metrics.get('peak_ram_kb', 'N/A')} KB | - | - |
| Total Memory | {metrics.get('flash_kb', 0) + (metrics.get('ram_kb') or metrics.get('peak_ram_kb', 0)) if metrics.get('flash_kb') and (metrics.get('ram_kb') or metrics.get('peak_ram_kb')) else 'N/A'} KB | < 300 KB | {"✅" if validation.get('memory_ok') else "❌" if validation.get('memory_ok') is False else "⏳"} |
| Inference Cycles | {metrics.get('cycles', 'N/A')} | - | - |

## Target Achievement

"""
    
    all_ok = all(v for v in validation.values() if v is not None)
    if all_ok:
        report += "✅ **All targets met**\n\n"
    else:
        report += "⚠️ **Some targets not met**\n\n"
        for key, value in validation.items():
            if value is False:
                report += f"- ❌ {key.replace('_', ' ').title()}\n"
    
    report += "\n## Notes\n\n"
    report += f"- Status: {benchmark.get('status', 'unknown')}\n"
    if benchmark.get('command'):
        report += f"- Command: `{benchmark['command']}`\n"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"[report] Benchmark report written to {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark models using Edge Impulse simulation.")
    parser.add_argument(
        "--model",
        type=Path,
        required=True,
        help="Path to model file (EIM or H5)",
    )
    parser.add_argument(
        "--target-mcu",
        type=str,
        default="cortex-m4f",
        help="Target MCU architecture",
    )
    parser.add_argument(
        "--frequency",
        type=int,
        default=80,
        help="MCU frequency in MHz",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output JSON benchmark file",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional markdown report path",
    )
    parser.add_argument(
        "--targets",
        type=Path,
        help="Path to targets JSON file",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    
    if not args.model.exists():
        raise FileNotFoundError(f"Model not found: {args.model}")
    
    # Calculate model size
    size_info = calculate_model_size(args.model)
    
    # Run simulation
    benchmark = run_edge_impulse_simulation(
        args.model,
        args.target_mcu,
        args.frequency
    )
    
    # Add size info to metrics
    benchmark["metrics"]["size_kb"] = size_info["size_kb"]
    benchmark["metrics"]["size_bytes"] = size_info["size_bytes"]
    
    # Load targets
    targets = {
        "latency_ms": 50.0,
        "model_size_kb": 300.0,
    }
    if args.targets and args.targets.exists():
        targets.update(json.loads(args.targets.read_text(encoding="utf-8")))
    
    # Validate
    validation = validate_targets(benchmark, targets)
    benchmark["validation"] = validation
    
    # Save benchmark JSON
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(benchmark, indent=2), encoding="utf-8")
    print(f"[benchmark] Results saved to {args.output}")
    
    # Generate report
    if args.report:
        generate_benchmark_report(benchmark, validation, args.report)
    
    # Print summary
    print("\n[benchmark] Summary:")
    print(f"  Model: {args.model.name}")
    print(f"  Size: {size_info['size_kb']:.2f} KB")
    if benchmark["metrics"].get("latency_ms"):
        print(f"  Latency: {benchmark['metrics']['latency_ms']} ms")
    print(f"  Targets met: {sum(1 for v in validation.values() if v)}/{sum(1 for v in validation.values() if v is not None)}")


if __name__ == "__main__":
    main()

