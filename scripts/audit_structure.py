#!/usr/bin/env python3
"""Project structure audit script.

Validates folder structure against expected layout and reports findings.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

# Define the expected folder structure
EXPECTED_STRUCTURE = {
    # Root level
    "ROOT": {
        "files": ["README.md", ".gitignore", ".env"],
        "folders": ["00_system", "01_planning", "02_dataset", "03_feature_pipeline", 
                   "04_models", "05_evaluation", "06_documentation", "07_demo",
                   "data", "docs", "notebooks", "scripts", "metadata", "logs",
                   "artifacts", "edge_impulse"],
    },
    
    # 02_dataset - Critical folder
    "02_dataset": {
        "files": ["README.md"],
        "folders": ["raw", "processed", "scripts", "splits", "licensing"],
    },
    
    "02_dataset/raw": {
        "files": ["metadata_raw.json"],
        "folders": ["audio_fire", "audio_non_fire", "sensor_fire"],
    },
    
    "02_dataset/raw/audio_fire": {
        "files": ["audioset_fire_crackle_branch.csv"],
        "folders": ["clips"],
    },
    
    "02_dataset/raw/audio_non_fire": {
        "files": [],
        "folders": ["UrbanSound8K"],
    },
    
    "02_dataset/raw/audio_non_fire/UrbanSound8K": {
        "files": [],
        "folders": ["audio", "metadata"],
    },
    
    "02_dataset/raw/sensor_fire": {
        "files": ["sensor_data.csv", "sensor_data.parquet", "sensor_metadata.json"],
        "folders": [],
    },
    
    "02_dataset/scripts": {
        "files": ["nasa_power_client.py", "noaa_client.py", "download_audioset.py", 
                 "fetch_sensor_data.py", "dataset_validate.py", "dataset_fetch.py",
                 "locations.csv"],
        "folders": [],
    },
    
    # 04_models
    "04_models": {
        "files": [],
        "folders": ["baseline", "advanced", "optimized", "logs"],
    },
    
    # 03_feature_pipeline
    "03_feature_pipeline": {
        "files": [],
        "folders": ["edge_impulse", "notebooks"],
    },
}

def check_structure(root_path: Path) -> Tuple[List[str], List[str], Dict]:
    """Check if folder structure matches expected layout."""
    issues = []
    checks_passed = []
    details = {}
    
    for path_key, expected in EXPECTED_STRUCTURE.items():
        if path_key == "ROOT":
            check_path = root_path
        else:
            check_path = root_path / path_key
        
        details[path_key] = {"exists": check_path.exists(), "missing_files": [], "missing_folders": []}
        
        # Check if path exists
        if not check_path.exists():
            issues.append(f"❌ Missing folder: {path_key}")
            continue
        
        # Check required files
        for file in expected.get("files", []):
            file_path = check_path / file
            if not file_path.exists():
                issues.append(f"❌ Missing file: {path_key}/{file}")
                details[path_key]["missing_files"].append(file)
            else:
                checks_passed.append(f"✅ Found: {path_key}/{file}")
        
        # Check required folders
        for folder in expected.get("folders", []):
            folder_path = check_path / folder
            if not folder_path.exists():
                issues.append(f"⚠️  Missing folder: {path_key}/{folder}")
                details[path_key]["missing_folders"].append(folder)
            else:
                checks_passed.append(f"✅ Found folder: {path_key}/{folder}")
    
    return issues, checks_passed, details


def main():
    root_path = Path("c:\\Users\\AADHITHAN\\Downloads\\WildGaurd-Edge")
    
    print("\n" + "="*80)
    print("PROJECT STRUCTURE AUDIT")
    print("="*80 + "\n")
    
    issues, passed, details = check_structure(root_path)
    
    # Print results
    print(f"📊 RESULTS: {len(passed)} checks passed, {len(issues)} issues found\n")
    
    if issues:
        print("⚠️  ISSUES FOUND:")
        print("-" * 80)
        for issue in issues:
            print(f"  {issue}")
        print()
    
    print("✅ CHECKS PASSED:")
    print("-" * 80)
    for check in passed[:20]:  # Show first 20
        print(f"  {check}")
    if len(passed) > 20:
        print(f"  ... and {len(passed) - 20} more checks")
    print()
    
    # Detailed summary
    print("📋 FOLDER STRUCTURE SUMMARY:")
    print("-" * 80)
    for path_key, detail in details.items():
        status = "✅" if detail["exists"] and not detail["missing_files"] else "⚠️"
        missing_info = ""
        if detail["missing_files"]:
            missing_info += f" (missing files: {', '.join(detail['missing_files'])})"
        if detail["missing_folders"]:
            missing_info += f" (missing folders: {', '.join(detail['missing_folders'])})"
        print(f"  {status} {path_key}{missing_info}")
    print()
    
    # Recommendations
    if issues:
        print("🔧 RECOMMENDATIONS:")
        print("-" * 80)
        print("  1. Create missing folders")
        print("  2. Move misplaced files to correct locations")
        print("  3. Update scripts that reference missing files")
        print("  4. Run validation again after fixes")
    else:
        print("✅ ALL CHECKS PASSED - Structure is correct!")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
