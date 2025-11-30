#!/usr/bin/env python3
"""
Complete optimization pipeline: quantize, prune, and benchmark.

Usage:
    python 04_models/optimized/optimize_pipeline.py \
        --input-model 04_models/advanced/versions/v2.0/model.h5 \
        --output-prefix v2.0_optimized \
        --quantize \
        --prune \
        --benchmark
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def run_quantization(input_model: Path, output_dir: Path, method: str) -> Path:
    """Run quantization step."""
    print(f"\n[1/3] Quantizing model...")
    cmd = [
        "python", "04_models/optimized/quantize_model.py",
        "--input-model", str(input_model),
        "--output-dir", str(output_dir),
        "--method", method,
        "--tool", "edge_impulse",
    ]
    subprocess.run(cmd, check=True)
    return output_dir / "model.eim"


def run_pruning(input_model: Path, output_dir: Path, sparsity: float) -> Path:
    """Run pruning step."""
    print(f"\n[2/3] Pruning model...")
    cmd = [
        "python", "04_models/optimized/prune_model.py",
        "--input-model", str(input_model),
        "--output-dir", str(output_dir),
        "--sparsity", str(sparsity),
        "--method", "magnitude",
    ]
    subprocess.run(cmd, check=True)
    return output_dir / "model_pruned.h5"


def run_benchmark(model_path: Path, output_path: Path) -> None:
    """Run benchmark step."""
    print(f"\n[3/3] Benchmarking model...")
    cmd = [
        "python", "04_models/optimized/benchmark_simulation.py",
        "--model", str(model_path),
        "--output", str(output_path),
        "--report", str(output_path.with_suffix(".md")),
    ]
    subprocess.run(cmd, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Complete optimization pipeline.")
    parser.add_argument(
        "--input-model",
        type=Path,
        required=True,
        help="Input model path",
    )
    parser.add_argument(
        "--output-prefix",
        type=str,
        required=True,
        help="Output prefix for optimized models",
    )
    parser.add_argument(
        "--quantize",
        action="store_true",
        help="Enable quantization",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Enable pruning",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run benchmark after optimization",
    )
    parser.add_argument(
        "--quantization-method",
        type=str,
        default="int8",
        help="Quantization method",
    )
    parser.add_argument(
        "--sparsity",
        type=float,
        default=0.5,
        help="Pruning sparsity",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    
    base_output = Path("04_models/optimized")
    current_model = args.input_model
    
    # Quantization
    if args.quantize:
        quantized_dir = base_output / "quantized" / f"{args.output_prefix}_int8"
        current_model = run_quantization(current_model, quantized_dir, args.quantization_method)
    
    # Pruning
    if args.prune:
        pruned_dir = base_output / "pruned" / f"{args.output_prefix}_pruned"
        current_model = run_pruning(current_model, pruned_dir, args.sparsity)
    
    # Benchmark
    if args.benchmark:
        benchmark_path = base_output / "benchmarks" / f"{args.output_prefix}_benchmark.json"
        run_benchmark(current_model, benchmark_path)
    
    print(f"\n[optimization] Pipeline complete!")
    print(f"[optimization] Final model: {current_model}")


if __name__ == "__main__":
    main()

