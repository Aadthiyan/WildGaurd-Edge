#!/usr/bin/env python3
"""
Download EmberSense datasets from their original sources.

This script helps download:
- AudioSet (wildfire subset)
- UrbanSound8K
- NASA/NOAA environmental sensor data

Usage:
    python 02_dataset/scripts/dataset_fetch.py --source audioset
    python 02_dataset/scripts/dataset_fetch.py --source urbansound8k
    python 02_dataset/scripts/dataset_fetch.py --source nasa --api-key YOUR_NASA_KEY
    python 02_dataset/scripts/dataset_fetch.py --all
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any


def download_audioset(output_dir: Path) -> Dict[str, Any]:
    """Download AudioSet wildfire subset."""
    print("[download] AudioSet wildfire subset")
    print("[download] Note: AudioSet requires manual download from Google Research")
    print("[download] Steps:")
    print("  1. Visit: https://research.google.com/audioset/")
    print("  2. Download the balanced train segments CSV")
    print("  3. Filter for ontology IDs: 528 (Fire), 520 (Crackle), 503 (Branch breaking)")
    print("  4. Use youtube-dl to download audio clips (respecting YouTube ToS)")
    print("  5. Place files in:", output_dir)
    
    # Create placeholder instructions
    readme_path = output_dir / "README_DOWNLOAD.md"
    readme_content = """# AudioSet Wildfire Subset Download Instructions

## Method 1: Manual Download (Recommended)

1. **Get AudioSet metadata**:
   - Visit: https://research.google.com/audioset/
   - Download "balanced_train_segments.csv"
   - Download "ontology.json" to understand label IDs

2. **Filter for wildfire-related sounds**:
   - Fire: ontology ID 528
   - Crackle: ontology ID 520
   - Branch breaking: ontology ID 503

3. **Download audio clips**:
   ```bash
   # Install youtube-dl
   pip install youtube-dl
   
   # Download clips (example - adjust CSV path)
   python scripts/download_audioset_clips.py \
       --csv balanced_train_segments.csv \
       --output-dir 02_dataset/raw/audio_fire \
       --ontology-ids 528 520 503
   ```

## Method 2: Use Pre-filtered Lists

Some researchers have created filtered lists. Search for:
- "AudioSet fire sounds"
- "AudioSet wildfire dataset"

## Important Notes

- Respect YouTube Terms of Service
- Check each video's license before downloading
- Some videos may be unavailable
- Download only for research purposes
- Follow CC BY 4.0 attribution requirements
"""
    readme_path.write_text(readme_content, encoding="utf-8")
    
    return {
        "source": "audioset",
        "status": "instructions_created",
        "readme": str(readme_path),
    }


def download_urbansound8k(output_dir: Path) -> Dict[str, Any]:
    """Download UrbanSound8K dataset."""
    print("[download] UrbanSound8K dataset")
    print("[download] Downloading from official source...")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # UrbanSound8K download URL
    url = "https://zenodo.org/record/1203745/files/UrbanSound8K.tar.gz"
    
    print(f"[download] URL: {url}")
    print("[download] Steps:")
    print("  1. Visit: https://urbansounddataset.weebly.com/urbansound8k.html")
    print("  2. Click 'Download Dataset'")
    print("  3. Extract to:", output_dir)
    print("  4. Or use wget/curl:")
    print(f"     wget {url} -O {output_dir}/UrbanSound8K.tar.gz")
    print(f"     tar -xzf {output_dir}/UrbanSound8K.tar.gz -C {output_dir}")
    
    # Create download script
    script_path = output_dir / "download.sh"
    script_content = f"""#!/bin/bash
# UrbanSound8K Download Script

OUTPUT_DIR="{output_dir}"
URL="https://zenodo.org/record/1203745/files/UrbanSound8K.tar.gz"

echo "Downloading UrbanSound8K..."
wget $URL -O "$OUTPUT_DIR/UrbanSound8K.tar.gz"

echo "Extracting..."
tar -xzf "$OUTPUT_DIR/UrbanSound8K.tar.gz" -C "$OUTPUT_DIR"

echo "Done! Files in: $OUTPUT_DIR/UrbanSound8K"
"""
    script_path.write_text(script_content, encoding="utf-8")
    script_path.chmod(0o755)
    
    # Windows batch script
    batch_path = output_dir / "download.bat"
    batch_content = f"""@echo off
REM UrbanSound8K Download Script for Windows

set OUTPUT_DIR={output_dir}
set URL=https://zenodo.org/record/1203745/files/UrbanSound8K.tar.gz

echo Downloading UrbanSound8K...
curl -L %URL% -o "%OUTPUT_DIR%\\UrbanSound8K.tar.gz"

echo.
echo Please extract UrbanSound8K.tar.gz to %OUTPUT_DIR%
echo You can use 7-Zip or WinRAR to extract .tar.gz files
"""
    batch_path.write_text(batch_content, encoding="utf-8")
    
    return {
        "source": "urbansound8k",
        "status": "scripts_created",
        "download_url": url,
        "scripts": [str(script_path), str(batch_path)],
    }


def download_nasa_data(output_dir: Path, api_key: str = None) -> Dict[str, Any]:
    """Download NASA/NOAA environmental sensor data."""
    print("[download] NASA/NOAA environmental sensor data")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not api_key:
        print("[download] NASA Earthdata requires API key")
        print("[download] Get one at: https://urs.earthdata.nasa.gov/")
        print("[download] Steps:")
        print("  1. Create account at https://urs.earthdata.nasa.gov/")
        print("  2. Generate API token")
        print("  3. Run: python 02_dataset/scripts/dataset_fetch.py --source nasa --api-key YOUR_KEY")
    
    # Create download script
    script_path = output_dir / "download_nasa.py"
    script_content = f"""#!/usr/bin/env python3
\"\"\"
Download NASA Earthdata environmental sensor data.

Requires:
- NASA Earthdata account: https://urs.earthdata.nasa.gov/
- API key/token
- Python packages: requests, pandas

Usage:
    python download_nasa.py --api-key YOUR_KEY --region california --year 2019
\"\"\"

import argparse
import requests
from pathlib import Path
import pandas as pd

def download_nasa_sensors(api_key: str, region: str, year: int, output_dir: Path):
    \"\"\"Download NASA sensor data for specified region and year.\"\"\"
    
    # Example API endpoints (adjust based on actual NASA API)
    # This is a template - actual endpoints vary by dataset
    
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    # Example parameters for fire-prone regions
    params = {{
        "parameters": "T2M,RH2M,PS,ALLSKY_SFC_SW_DWN",
        "community": "RE",
        "longitude": -120.0,  # California example
        "latitude": 37.0,
        "start": f"{{year}}0101",
        "end": f"{{year}}1231",
        "format": "JSON",
        "api_key": api_key
    }}
    
    print(f"Downloading data for {{region}} {{year}}...")
    # response = requests.get(base_url, params=params)
    # Process and save data
    
    print("See NASA Earthdata documentation for specific dataset APIs:")
    print("  - POWER: https://power.larc.nasa.gov/")
    print("  - MODIS: https://modis.gsfc.nasa.gov/data/")
    print("  - Landsat: https://landsat.gsfc.nasa.gov/data/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--region", default="california")
    parser.add_argument("--year", type=int, default=2019)
    parser.add_argument("--output-dir", type=Path, default=Path("{output_dir}"))
    args = parser.parse_args()
    
    download_nasa_sensors(args.api_key, args.region, args.year, args.output_dir)
"""
    script_path.write_text(script_content, encoding="utf-8")
    
    readme_path = output_dir / "README_NASA.md"
    readme_content = """# NASA/NOAA Environmental Sensor Data Download

## NASA Earthdata

1. **Create Account**: https://urs.earthdata.nasa.gov/
2. **Get API Token**: Profile → Generate Token
3. **Available Datasets**:
   - POWER (Prediction of Worldwide Energy Resources): Temperature, humidity, pressure
   - MODIS: Fire detection, land surface temperature
   - Landsat: Land surface data

## NOAA Data

1. **NOAA Climate Data**: https://www.ncdc.noaa.gov/
2. **NOAA API**: https://www.ncdc.noaa.gov/cdo-web/webservices/v2
3. **Get API Key**: https://www.ncdc.noaa.gov/cdo-web/token

## Recommended Datasets for EmberSense

- **Temperature & Humidity**: NASA POWER API
- **VOC Data**: May need to use simulated/synthetic data
- **Barometric Pressure**: NASA POWER or NOAA

## Download Script

```bash
python download_nasa.py --api-key YOUR_KEY --region california --year 2019
```

## Alternative: Use Pre-processed Data

For quick testing, you can use:
- Synthetic sensor data (generated)
- Public weather station data
- Historical fire event data with environmental conditions
"""
    readme_path.write_text(readme_content, encoding="utf-8")
    
    return {
        "source": "nasa",
        "status": "scripts_created",
        "requires_api_key": True,
        "readme": str(readme_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download EmberSense datasets.")
    parser.add_argument(
        "--source",
        type=str,
        choices=["audioset", "urbansound8k", "nasa", "all"],
        help="Dataset source to download",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="API key for NASA downloads",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("02_dataset/raw"),
        help="Base output directory",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    
    if not args.source:
        print("Available datasets:")
        print("  --source audioset      : AudioSet wildfire subset")
        print("  --source urbansound8k  : UrbanSound8K negative samples")
        print("  --source nasa          : NASA/NOAA environmental sensors")
        print("  --source all           : Download all datasets")
        print()
        print("Example:")
        print("  python 02_dataset/scripts/dataset_fetch.py --source urbansound8k")
        return
    
    results = []
    
    if args.source in ["audioset", "all"]:
        output_dir = args.output_dir / "audio_fire"
        output_dir.mkdir(parents=True, exist_ok=True)
        result = download_audioset(output_dir)
        results.append(result)
    
    if args.source in ["urbansound8k", "all"]:
        output_dir = args.output_dir / "audio_non_fire"
        output_dir.mkdir(parents=True, exist_ok=True)
        result = download_urbansound8k(output_dir)
        results.append(result)
    
    if args.source in ["nasa", "all"]:
        output_dir = args.output_dir / "sensor_fire"
        output_dir.mkdir(parents=True, exist_ok=True)
        result = download_nasa_data(output_dir, args.api_key)
        results.append(result)
    
    # Save download log
    log_path = args.output_dir / "download_log.json"
    log_data = {
        "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": results,
    }
    log_path.write_text(json.dumps(log_data, indent=2), encoding="utf-8")
    
    print("\n[download] Summary:")
    for result in results:
        print(f"  {result['source']}: {result['status']}")
    print(f"\n[download] Log saved to: {log_path}")


if __name__ == "__main__":
    main()

