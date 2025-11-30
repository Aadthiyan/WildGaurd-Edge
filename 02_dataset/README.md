# EmberSense Dataset Directory

## Overview

This directory contains raw and processed datasets for EmberSense wildfire detection. **Note: Datasets are not included in the repository** - you need to download them from their original sources.

## Quick Start: Downloading Datasets

### Option 1: Use Download Script
```bash
# Download UrbanSound8K (easiest)
python 02_dataset/scripts/dataset_fetch.py --source urbansound8k

# Download all datasets (with instructions)
python 02_dataset/scripts/dataset_fetch.py --source all
```

### Option 2: Manual Download

#### 1. UrbanSound8K (Negative Audio Samples)
- **URL**: https://urbansounddataset.weebly.com/urbansound8k.html
- **Download**: Click "Download Dataset" button
- **Extract to**: `02_dataset/raw/audio_non_fire/`
- **Size**: ~6 GB
- **License**: CC BY 4.0

#### 2. AudioSet (Wildfire Audio)
- **URL**: https://research.google.com/audioset/
- **Steps**:
  1. Download "balanced_train_segments.csv"
  2. Filter for ontology IDs: 528 (Fire), 520 (Crackle), 503 (Branch breaking)
  3. Use youtube-dl to download clips (respect YouTube ToS)
  4. Place in: `02_dataset/raw/audio_fire/`
- **License**: CC BY 4.0 (check individual video licenses)
- **Current Status**: CSV manifest available (`audioset_fire_crackle_branch.csv`)
- **Next Step**: Download audio clips using the automated downloader:
  
  ```bash
  # Test with 10 clips first
  python 02_dataset/scripts/download_audioset.py \\
    --csv 02_dataset/raw/audio_fire/audioset_fire_crackle_branch.csv \\
    --output-dir 02_dataset/raw/audio_fire/clips \\
    --max-downloads 10 \\
    --max-workers 2
  
  # Download all clips (may take a while depending on internet)
  python 02_dataset/scripts/download_audioset.py \\
    --csv 02_dataset/raw/audio_fire/audioset_fire_crackle_branch.csv \\
    --output-dir 02_dataset/raw/audio_fire/clips \\
    --max-workers 4
  ```
  
- **Note**: Requires `yt-dlp` and `ffmpeg`:
  ```bash
  pip install yt-dlp
  # ffmpeg: download from https://ffmpeg.org/download.html or conda install ffmpeg
  ```

#### 3. NASA/NOAA Environmental Sensors
 - **NASA Earthdata**: https://urs.earthdata.nasa.gov/
   - Create account and get API key
   - Use POWER API for temperature, humidity, pressure
 - **NOAA**: https://www.ncdc.noaa.gov/cdo-web/
   - Get API key from https://www.ncdc.noaa.gov/cdo-web/token
 - **Place data in**: `02_dataset/raw/sensor_fire/`
 - **Format**: Parquet or CSV

### NASA POWER API — public & registered access

The NASA POWER API (https://power.larc.nasa.gov/api/) provides global climate and weather data (temperature, humidity, pressure, solar radiation, etc.) at daily, hourly, monthly, or climatology resolutions.

- **Public data**: No API key required. Simply use the API endpoints directly.
- **Restricted data**: Requires Earthdata login (which you've already created at https://urs.earthdata.nasa.gov/).

#### Getting Started

1. Verify your Earthdata account is active at https://urs.earthdata.nasa.gov/.
2. Use the Python client in `02_dataset/scripts/nasa_power_client.py` to fetch data:

   ```python
   from nasa_power_client import get_power_data
   
   # Public data (no auth needed)
   data = get_power_data(
       latitude=38.0, longitude=-77.0,
       start_date="20210101", end_date="20210131",
       temporal_api="daily",
       parameters=["T2M", "RH2M", "ALLSKY_SFC_SW_DWN"]
   )

   # Restricted data (if needed)
   data = get_power_data(
       latitude=38.0, longitude=-77.0,
       start_date="20210101", end_date="20210131",
       temporal_api="hourly",
       parameters=["T2M"],
       username="your_earthdata_username",
       password="your_earthdata_password"
   )
   ```

3. Or use it from the command line:

   ```bash
   python 02_dataset/scripts/nasa_power_client.py
   ```

#### Common Parameters

- `T2M`: 2-meter air temperature (K)
- `RH2M`: Relative humidity at 2 meters (%)
- `PS`: Surface pressure (kPa)
- `ALLSKY_SFC_SW_DWN`: All-sky surface shortwave downward irradiance (W/m²)
- `PRECTOTCORR`: Precipitation (mm/day)

See https://power.larc.nasa.gov/docs/services/api/temporal/hourly/ for the full parameter list.

#### Rate Limits

- The NASA POWER API has no per-user rate limit for public data.
- Response times vary by temporal level (hourly > daily > monthly) and number of parameters.
- The client includes automatic retry logic with exponential backoff for `429` (rate limit) responses.

### Bulk Sensor Data Fetcher

To automatically download and combine NASA POWER and NOAA data for multiple locations:

1. **Edit the locations CSV** (`02_dataset/scripts/locations.csv`):
   ```csv
   name,latitude,longitude
   california_fire,38.5,-120.5
   australia_fire,-35.2,142.5
   ```

2. **Run the bulk fetcher**:
   ```bash
   python 02_dataset/scripts/fetch_sensor_data.py \
     --locations-csv 02_dataset/scripts/locations.csv \
     --start-date 2020-01-01 \
     --end-date 2020-12-31 \
     --output-dir 02_dataset/raw/sensor_fire \
     --sources nasa,noaa
   ```

3. **Output**:
   - `sensor_data.csv` — Combined sensor data from all sources
   - `sensor_data.parquet` — Same data in Parquet format (more efficient)
   - `sensor_metadata.json` — Metadata about the fetch operation

The fetcher automatically:
- Combines NASA POWER and NOAA data
- Handles API retries and rate limits
- Saves in both CSV and Parquet for flexibility
- Creates metadata for reproducibility### NOAA API Key — secure storage

When using NOAA's CDO web services you will receive an API token. Do NOT commit that token into the repo. Store it securely and read it from environment variables or a secrets manager.

- **Recommended (environment variable)**: set `NOAA_API_KEY` for your user or CI environment.

  PowerShell (session):

  ```powershell
  $env:NOAA_API_KEY = 'YOUR_NOAA_API_KEY'
  ```

  PowerShell (persist for user):

  ```powershell
  setx NOAA_API_KEY "YOUR_NOAA_API_KEY"
  ```

- **Alternative (.env file)**: create a top-level `.env` with the key and add `.env` to `.gitignore` (do not commit `.env`):

  ```text
  NOAA_API_KEY=YOUR_NOAA_API_KEY
  ```

- **Best practice**: use your cloud or OS secrets manager (Azure Key Vault, AWS Secrets Manager, Windows Credential Manager) for CI and production.

Example usage in code: read `NOAA_API_KEY` from the environment and pass it in the `token` header for NOAA CDO requests.

See `02_dataset/scripts/noaa_client.py` for a small example client.

## Directory Structure

```
02_dataset/
├── raw/
│   ├── audio_fire/          # Fire-positive audio samples
│   ├── audio_non_fire/      # Negative audio samples (UrbanSound8K)
│   ├── sensor_fire/         # Environmental sensor data
│   └── metadata_raw.json    # Dataset manifest
├── processed/
│   ├── cleaned_audio/       # Processed audio files
│   ├── cleaned_sensor/      # Processed sensor data
│   ├── annotations.csv      # Audio event annotations
│   └── dataset_summary.json # Dataset statistics
├── splits/
│   └── dataset_splits.json  # Train/val/test splits
├── scripts/
│   ├── dataset_fetch.py     # Download scripts
│   ├── dataset_validate.py  # Validation scripts
│   └── preprocess_audio.py  # Preprocessing scripts
└── licensing/
    └── dataset_licenses.md  # License information
```

## Dataset Sources

### AudioSet Wildfire Subset
- **Source**: Google Research AudioSet
- **License**: CC BY 4.0
- **Expected items**: ~1,200 clips
- **Labels**: fire, crackle, branch_break, combustion_pop
- **Download instructions**: See `raw/audio_fire/README_DOWNLOAD.md`

### UrbanSound8K
- **Source**: https://urbansounddataset.weebly.com/
- **License**: CC BY 4.0
- **Expected items**: 8,732 audio files
- **Labels**: Various urban/environmental sounds (used as negatives)
- **Download**: Direct download available

### NASA/NOAA Environmental Sensors
- **Source**: NASA Earthdata / NOAA
- **License**: Public Domain
- **Expected items**: ~520 sensor segments
- **Channels**: temperature, humidity, VOC, barometric_pressure
- **Download instructions**: See `raw/sensor_fire/README_NASA.md`

## Alternative: Use Synthetic Data for Testing

If you want to test the pipeline without downloading large datasets:

```bash
# Generate synthetic data for testing
python 02_dataset/scripts/generate_synthetic_data.py \
    --audio-samples 100 \
    --sensor-segments 50 \
    --output-dir 02_dataset/raw
```

## Validation

After downloading, validate your datasets:

```bash
# Check dataset completeness
python 02_dataset/scripts/dataset_validate.py \
    --manifest 02_dataset/raw/metadata_raw.json \
    --report 05_evaluation/reports/dataset_completeness.json

# Check licenses
python 02_dataset/scripts/check_dataset_licenses.py \
    --manifest 02_dataset/raw/metadata_raw.json \
    --registry 02_dataset/licensing/dataset_licenses.md
```

## Next Steps

1. **Download datasets** using the scripts or manual methods above
2. **Upload to Edge Impulse Studio** (see `docs/EDGE_IMPULSE_SETUP.md`)
3. **Run preprocessing** (see `02_dataset/scripts/preprocess_audio.py`)
4. **Validate** datasets before training

## Need Help?

- See `docs/EDGE_IMPULSE_SETUP.md` for Edge Impulse upload instructions
- Check individual README files in each raw data subdirectory
- Review `02_dataset/licensing/dataset_licenses.md` for license requirements

