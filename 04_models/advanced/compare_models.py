#!/usr/bin/env python3
"""
Compare baseline and advanced models across accuracy, memory, and latency metrics.

Usage:
    python 04_models/advanced/compare_models.py \
        --baseline 04_models/baseline/baseline_performance.json \
        --advanced 04_models/advanced/versions/v2.0/version_metadata.json \
        --output 05_evaluation/reports/comparative_report.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import pandas as pd


def load_performance_data(file_path: Path) -> Dict:
    """Load model performance data from JSON."""
    data = json.loads(file_path.read_text(encoding="utf-8"))
    
    # Handle different JSON structures
    if "models" in data:
        # Baseline format with multiple models
        return data
    elif "results" in data:
        # Advanced model format
        return {"models": [data]}
    else:
        # Single model format
        return {"models": [data]}


def extract_metrics(model_data: Dict) -> Dict:
    """Extract key metrics from model data."""
    if isinstance(model_data, list):
        model_data = model_data[0] if model_data else {}
    
    # Try different possible key structures
    results = model_data.get("results", {})
    metrics = {
        "name": model_data.get("model_name") or model_data.get("name", "unknown"),
        "version": model_data.get("version", "unknown"),
        "accuracy": results.get("accuracy") or model_data.get("accuracy"),
        "f1_macro": results.get("f1_macro") or model_data.get("f1_macro"),
        "latency_ms": results.get("latency_ms") or model_data.get("latency_ms"),
        "flash_kb": results.get("flash_kb") or model_data.get("flash_kb"),
        "ram_kb": results.get("ram_kb") or model_data.get("ram_kb"),
        "memory_total_kb": None,
    }
    
    # Calculate total memory
    if metrics["flash_kb"] and metrics["ram_kb"]:
        metrics["memory_total_kb"] = metrics["flash_kb"] + metrics["ram_kb"]
    
    return metrics


def compare_models(baseline_data: Dict, advanced_data: Dict) -> pd.DataFrame:
    """Create comparison DataFrame."""
    baseline_models = baseline_data.get("models", [])
    advanced_models = advanced_data.get("models", [])
    
    all_metrics = []
    
    # Add baseline models
    for model in baseline_models:
        metrics = extract_metrics(model)
        metrics["category"] = "baseline"
        all_metrics.append(metrics)
    
    # Add advanced models
    for model in advanced_models:
        metrics = extract_metrics(model)
        metrics["category"] = "advanced"
        all_metrics.append(metrics)
    
    df = pd.DataFrame(all_metrics)
    return df


def generate_markdown_report(df: pd.DataFrame, output_path: Path) -> None:
    """Generate markdown comparative report."""
    report = f"""# EmberSense Model Comparative Report

Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

This report compares baseline and advanced model variants across key performance metrics.

## Metrics Comparison

### Accuracy

| Model | Version | Category | Accuracy | F1 Macro |
|-------|---------|----------|----------|----------|
"""
    
    for _, row in df.iterrows():
        acc = row.get("accuracy", "N/A")
        f1 = row.get("f1_macro", "N/A")
        if isinstance(acc, float):
            acc = f"{acc:.2%}"
        if isinstance(f1, float):
            f1 = f"{f1:.2%}"
        report += f"| {row['name']} | {row['version']} | {row['category']} | {acc} | {f1} |\n"
    
    report += "\n### Resource Usage\n\n"
    report += "| Model | Version | Latency (ms) | Flash (KB) | RAM (KB) | Total Memory (KB) |\n"
    report += "|-------|---------|--------------|------------|----------|-------------------|\n"
    
    for _, row in df.iterrows():
        latency = row.get("latency_ms", "N/A")
        flash = row.get("flash_kb", "N/A")
        ram = row.get("ram_kb", "N/A")
        total = row.get("memory_total_kb", "N/A")
        report += f"| {row['name']} | {row['version']} | {latency} | {flash} | {ram} | {total} |\n"
    
    report += "\n## Target Metrics\n\n"
    report += "- **Accuracy**: ≥ 85%\n"
    report += "- **Latency**: < 50 ms\n"
    report += "- **Memory**: < 300 KB (total)\n\n"
    
    # Check which models meet targets
    report += "## Target Achievement\n\n"
    for _, row in df.iterrows():
        meets_accuracy = isinstance(row.get("accuracy"), float) and row["accuracy"] >= 0.85
        meets_latency = isinstance(row.get("latency_ms"), (int, float)) and row["latency_ms"] < 50
        meets_memory = isinstance(row.get("memory_total_kb"), (int, float)) and row["memory_total_kb"] < 300
        
        all_met = meets_accuracy and meets_latency and meets_memory
        status = "✅" if all_met else "⚠️"
        report += f"- **{row['name']} v{row['version']}**: {status}\n"
        if not all_met:
            issues = []
            if not meets_accuracy:
                issues.append("accuracy")
            if not meets_latency:
                issues.append("latency")
            if not meets_memory:
                issues.append("memory")
            report += f"  - Issues: {', '.join(issues)}\n"
    
    report += "\n## Recommendations\n\n"
    
    # Find best model
    if "accuracy" in df.columns and df["accuracy"].notna().any():
        best_acc = df.loc[df["accuracy"].idxmax()]
        report += f"- **Best Accuracy**: {best_acc['name']} v{best_acc['version']} ({best_acc['accuracy']:.2%})\n"
    
    if "latency_ms" in df.columns and df["latency_ms"].notna().any():
        best_latency = df.loc[df["latency_ms"].idxmin()]
        report += f"- **Best Latency**: {best_latency['name']} v{best_latency['version']} ({best_latency['latency_ms']} ms)\n"
    
    if "memory_total_kb" in df.columns and df["memory_total_kb"].notna().any():
        best_memory = df.loc[df["memory_total_kb"].idxmin()]
        report += f"- **Best Memory**: {best_memory['name']} v{best_memory['version']} ({best_memory['memory_total_kb']} KB)\n"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"[report] Comparative report written to {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare baseline and advanced models.")
    parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
        help="Path to baseline performance JSON",
    )
    parser.add_argument(
        "--advanced",
        type=Path,
        nargs="+",
        help="Path(s) to advanced model metadata JSON(s)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output markdown report path",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        help="Optional CSV output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    
    # Load baseline
    baseline_data = load_performance_data(args.baseline)
    
    # Load advanced models
    advanced_models = []
    if args.advanced:
        for adv_path in args.advanced:
            adv_data = load_performance_data(adv_path)
            advanced_models.extend(adv_data.get("models", [adv_data]))
    
    advanced_data = {"models": advanced_models}
    
    # Compare
    df = compare_models(baseline_data, advanced_data)
    
    # Generate report
    generate_markdown_report(df, args.output)
    
    # Optionally save CSV
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(args.csv, index=False)
        print(f"[csv] Comparison data saved to {args.csv}")


if __name__ == "__main__":
    main()

