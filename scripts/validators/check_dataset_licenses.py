#!/usr/bin/env python3
"""
Cross-check dataset licenses against the registry markdown.

Usage:
    python scripts/validators/check_dataset_licenses.py \
        --manifest metadata/dataset_manifest.json \
        --registry docs/licenses/dataset_licenses.md \
        --report artifacts/week1/license_audit.json
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Dict, List


def load_registry(registry_path: Path) -> str:
    return registry_path.read_text(encoding="utf-8")


def validate_license_entries(
    manifest_sources: List[Dict], registry_text: str
) -> List[Dict]:
    results: List[Dict] = []
    for source in manifest_sources:
        license_name = source.get("license", "").strip()
        source_name = source.get("name", "UNKNOWN")
        issues: List[str] = []

        if not license_name:
            issues.append("License field missing in manifest.")
        else:
            license_pattern = re.escape(license_name)
            if not re.search(license_pattern, registry_text, re.IGNORECASE):
                issues.append(
                    f"License '{license_name}' not documented in registry."
                )

        if source_name not in registry_text:
            issues.append(
                f"Source '{source_name}' missing from registry markdown."
            )

        status = "pass" if not issues else "attention"
        results.append(
            {
                "source_id": source.get("id"),
                "license": license_name or "UNSPECIFIED",
                "status": status,
                "issues": issues,
            }
        )
    return results


def run_audit(manifest_path: Path, registry_path: Path) -> Dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    registry_text = load_registry(registry_path)
    manifest_sources = manifest.get("sources", [])
    results = validate_license_entries(manifest_sources, registry_text)
    return {
        "audited_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "manifest_version": manifest.get("version"),
        "registry": str(registry_path),
        "results": results,
    }


def write_report(report: Dict, report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify dataset licenses are documented."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="Path to dataset_manifest.json",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        required=True,
        help="Path to dataset license registry markdown",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional JSON report path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_audit(args.manifest, args.registry)
    if args.report:
        write_report(report, args.report)
        print(f"[license-check] Report written to {args.report}")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

