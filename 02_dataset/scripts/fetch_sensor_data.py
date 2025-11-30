#!/usr/bin/env python3
"""Bulk sensor data fetcher for wildfire detection datasets.

Combines NASA POWER API and NOAA CDO API to fetch environmental sensor data
(temperature, humidity, pressure, solar radiation) for specified locations
and date ranges.

Usage:
    python fetch_sensor_data.py \\
        --locations-csv locations.csv \\
        --start-date 2021-01-01 \\
        --end-date 2021-12-31 \\
        --output-dir 02_dataset/raw/sensor_fire/

locations.csv format:
    name,latitude,longitude
    california_fire,38.0,-120.5
    australia_fire,-35.2,142.5
"""

import os
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

import pandas as pd

# Import the clients
import sys
sys.path.insert(0, str(Path(__file__).parent))

from nasa_power_client import get_power_data
from noaa_client import get_noaa_data


def parse_date(date_str: str) -> str:
    """Convert YYYY-MM-DD to YYYYMMDD format."""
    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        return date_str.replace('-', '')
    return date_str


def fetch_nasa_power_data(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    location_name: str = "point",
) -> pd.DataFrame:
    """Fetch NASA POWER daily data for a location."""
    print(f"  [NASA POWER] Fetching {location_name} ({latitude}, {longitude})...")
    
    try:
        data = get_power_data(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
            temporal_api="daily",
            parameters=["T2M", "RH2M", "PS", "ALLSKY_SFC_SW_DWN", "PRECTOTCORR"],
            community="SB",
        )
        
        # Parse the response
        if "properties" in data and "parameter" in data["properties"]:
            records = []
            params = data["properties"]["parameter"]
            times = data.get("times", {})
            
            # Extract data for each parameter
            for param_name, param_data in params.items():
                for date_key, value in param_data.items():
                    # Convert YYYYMMDD to datetime
                    try:
                        date_obj = datetime.strptime(date_key, "%Y%m%d")
                    except ValueError:
                        continue
                    
                    # Check if this record already exists
                    matching = [r for r in records if r.get("date") == date_obj]
                    if matching:
                        matching[0][param_name] = value
                    else:
                        records.append({
                            "date": date_obj,
                            "location": location_name,
                            "latitude": latitude,
                            "longitude": longitude,
                            param_name: value,
                            "source": "NASA_POWER",
                        })
            
            df = pd.DataFrame(records)
            print(f"  ✅ NASA POWER: {len(df)} records")
            return df
        else:
            print(f"  ⚠️ Unexpected NASA POWER response format")
            return pd.DataFrame()
    except Exception as e:
        print(f"  ❌ NASA POWER error: {e}")
        return pd.DataFrame()


def fetch_noaa_data(
    location_name: str,
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """Fetch NOAA station data (if available for the location)."""
    print(f"  [NOAA] Searching for stations near {location_name}...")
    
    try:
        # Find nearby stations (GHCND = daily summaries)
        stations = get_noaa_data(
            "stations",
            params={
                "datasetid": "GHCND",
                "extent": f"{latitude-0.5},{longitude-0.5},{latitude+0.5},{longitude+0.5}",
                "limit": 10,
            },
        )
        
        if not stations.get("results"):
            print(f"  ⚠️ No NOAA stations found near {location_name}")
            return pd.DataFrame()
        
        # Use the closest station
        station_id = stations["results"][0]["id"]
        station_name = stations["results"][0]["name"]
        print(f"  Using station: {station_name}")
        
        # Fetch data from the station
        data = get_noaa_data(
            "data",
            params={
                "datasetid": "GHCND",
                "stationid": station_id,
                "startDate": start_date,
                "endDate": end_date,
                "limit": 1000,
            },
        )
        
        if not data.get("results"):
            print(f"  ⚠️ No NOAA data available for {station_id}")
            return pd.DataFrame()
        
        records = []
        for result in data["results"]:
            records.append({
                "date": datetime.fromisoformat(result["date"][:10]),
                "location": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "datatype": result["datatype"],
                "value": result["value"],
                "unit": result.get("attributes", ""),
                "source": "NOAA",
            })
        
        df = pd.DataFrame(records)
        print(f"  ✅ NOAA: {len(df)} records")
        return df
    except Exception as e:
        print(f"  ❌ NOAA error: {e}")
        return pd.DataFrame()


def main():
    parser = argparse.ArgumentParser(description="Fetch sensor data from NASA POWER and NOAA")
    parser.add_argument(
        "--locations-csv",
        type=str,
        default="locations.csv",
        help="CSV file with columns: name, latitude, longitude",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default="2020-01-01",
        help="Start date (YYYY-MM-DD or YYYYMMDD)",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default="2020-12-31",
        help="End date (YYYY-MM-DD or YYYYMMDD)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="02_dataset/raw/sensor_fire",
        help="Output directory for sensor data",
    )
    parser.add_argument(
        "--sources",
        type=str,
        default="nasa,noaa",
        help="Comma-separated sources: nasa,noaa",
    )
    
    args = parser.parse_args()
    
    # Convert dates to YYYYMMDD format
    start_date = parse_date(args.start_date)
    end_date = parse_date(args.end_date)
    
    # Create output directory (resolve to absolute path)
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load locations
    if not Path(args.locations_csv).exists():
        print(f"Error: {args.locations_csv} not found")
        print("Please create a CSV with columns: name, latitude, longitude")
        return
    
    locations = []
    with open(args.locations_csv) as f:
        reader = csv.DictReader(f)
        locations = list(reader)
    
    if not locations:
        print(f"No locations found in {args.locations_csv}")
        return
    
    print(f"Fetching sensor data for {len(locations)} locations")
    print(f"Date range: {start_date} to {end_date}\n")
    
    all_dfs = []
    sources = set(args.sources.lower().split(","))
    
    # Fetch data for each location
    for loc in locations:
        name = loc["name"]
        lat = float(loc["latitude"])
        lon = float(loc["longitude"])
        
        print(f"Location: {name} ({lat}, {lon})")
        
        if "nasa" in sources:
            nasa_df = fetch_nasa_power_data(lat, lon, start_date, end_date, name)
            all_dfs.append(nasa_df)
        
        if "noaa" in sources:
            noaa_df = fetch_noaa_data(name, lat, lon, start_date, end_date)
            all_dfs.append(noaa_df)
        
        print()
    
    # Combine and save
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        # Save as CSV and Parquet
        csv_path = output_dir / "sensor_data.csv"
        parquet_path = output_dir / "sensor_data.parquet"
        
        combined_df.to_csv(csv_path, index=False)
        combined_df.to_parquet(parquet_path, index=False)
        
        print(f"✅ Saved {len(combined_df)} total records")
        print(f"   CSV: {csv_path}")
        print(f"   Parquet: {parquet_path}")
        
        # Create metadata
        metadata = {
            "sources": list(sources),
            "locations": len(locations),
            "start_date": start_date,
            "end_date": end_date,
            "total_records": len(combined_df),
            "created": datetime.now().isoformat(),
        }
        
        metadata_path = output_dir / "sensor_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"   Metadata: {metadata_path}")
    else:
        print("❌ No data fetched")


if __name__ == "__main__":
    main()
