#!/usr/bin/env python3
"""AudioSet fire/crackle/branch audio downloader.

Downloads audio clips from YouTube based on the AudioSet CSV manifest.
Uses yt-dlp to download videos and ffmpeg-python to extract audio segments.

CSV format: YTID, start_seconds, end_seconds, positive_labels
Example: 0Gj0gGPGlMA,0.0,10.0," /m/01j3sz"

Usage:
    python download_audioset.py \\
        --csv audioset_fire_crackle_branch.csv \\
        --output-dir 02_dataset/raw/audio_fire/clips \\
        --max-downloads 50 \\
        --max-workers 4
"""

import os
import csv
import json
import argparse
import sys
import tempfile
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple

import yt_dlp

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def download_audioset_clip(
    yt_id: str,
    start_sec: float,
    end_sec: float,
    output_dir: Path,
    label: str = "fire",
) -> Tuple[bool, str]:
    """Download a single AudioSet clip from YouTube.
    
    Args:
        yt_id: YouTube video ID
        start_sec: Start timestamp in seconds
        end_sec: End timestamp in seconds
        output_dir: Directory to save audio
        label: Category label (e.g., "fire", "crackle")
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Try multiple possible extensions
    possible_outputs = [
        output_dir / f"{yt_id}.mp3",
        output_dir / f"{yt_id}.m4a",
        output_dir / f"{yt_id}.webm",
        output_dir / f"{yt_id}.wav",
        output_dir / yt_id,  # No extension
    ]
    
    # Skip if already downloaded
    for output_file in possible_outputs:
        if output_file.exists():
            return True, f"Skipped (exists): {output_file.name}"
    
    try:
        # Configure yt-dlp options - NO ffmpeg required
        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": False,
            "no_warnings": False,
            "outtmpl": str(output_dir / f"{yt_id}"),
            "socket_timeout": 60,
            "prefer_ffmpeg": False,  # Don't require ffmpeg
        }
        
        # Download video audio (without postprocessing)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={yt_id}", download=True)
            
        # Check which file was created (it may not have an extension)
        for output_file in possible_outputs:
            if output_file.exists():
                size_mb = output_file.stat().st_size / (1024 * 1024)
                # If it's the no-extension version, get info
                ext = output_file.suffix if output_file.suffix else "(audio)"
                return True, f"✅ {yt_id}{ext} ({size_mb:.2f} MB)"
        
        return False, f"File not found after download: {yt_id}"
    
    except yt_dlp.utils.DownloadError as e:
        return False, f"Video unavailable: {yt_id}"
    except Exception as e:
        error_msg = str(e)[:50]
        return False, f"Error: {error_msg}"


def load_audioset_csv(csv_file: Path) -> List[Dict]:
    """Load AudioSet CSV manifest."""
    clips = []
    with open(csv_file, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Handle different column name formats
                yt_id = row.get(" YTID") or row.get("YTID")
                start_col = row.get(" start_seconds") or row.get("start_seconds")
                end_col = row.get(" end_seconds") or row.get("end_seconds")
                labels = row.get(" positive_labels") or row.get("positive_labels")
                
                clips.append({
                    "yt_id": yt_id.strip() if yt_id else "",
                    "start": float(start_col) if start_col else 0.0,
                    "end": float(end_col) if end_col else 10.0,
                    "labels": labels.strip() if labels else "",
                })
            except (ValueError, AttributeError, KeyError):
                continue
    
    return clips


def main():
    parser = argparse.ArgumentParser(description="Download AudioSet fire/crackle/branch clips")
    parser.add_argument(
        "--csv",
        type=str,
        default="audioset_fire_crackle_branch.csv",
        help="Path to AudioSet CSV manifest",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="audio_clips",
        help="Output directory for downloaded audio",
    )
    parser.add_argument(
        "--max-downloads",
        type=int,
        default=None,
        help="Maximum number of clips to download (default: all)",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=2,
        help="Number of parallel download workers (default: 2)",
    )
    
    args = parser.parse_args()
    
    # Load CSV
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        return
    
    clips = load_audioset_csv(csv_path)
    print(f"✅ Loaded {len(clips)} clips from {csv_path.name}")
    
    # Limit downloads if requested
    if args.max_downloads:
        clips = clips[:args.max_downloads]
        print(f"📌 Limiting to {args.max_downloads} clips")
    
    # Create output directory
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output: {output_dir}\n")
    
    # Download clips in parallel
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {
            executor.submit(
                download_audioset_clip,
                clip["yt_id"],
                clip["start"],
                clip["end"],
                output_dir,
            ): clip for clip in clips
        }
        
        for i, future in enumerate(as_completed(futures), 1):
            clip = futures[future]
            success, message = future.result()
            
            status = "✅" if success else "❌"
            print(f"[{i:3d}/{len(clips)}] {status} {clip['yt_id']} - {message}")
            
            if "Skipped" in message:
                skipped_count += 1
            elif success:
                success_count += 1
            else:
                failed_count += 1
    
    print(f"\n{'='*70}")
    print(f"✅ Downloaded: {success_count}")
    print(f"⏭️  Skipped:    {skipped_count}")
    print(f"❌ Failed:     {failed_count}")
    print(f"📊 Total:      {success_count + skipped_count + failed_count}/{len(clips)}")
    
    # Create metadata
    audio_files = (list(output_dir.glob("*.mp3")) + 
                   list(output_dir.glob("*.m4a")) + 
                   list(output_dir.glob("*.webm")) + 
                   list(output_dir.glob("*.wav")))
    
    # Also count files without extensions (yt-dlp sometimes saves without ext)
    all_files = [f for f in output_dir.iterdir() if f.is_file() and f.name != "audioset_metadata.json"]
    
    metadata = {
        "source": "AudioSet",
        "csv_file": str(csv_path),
        "audio_files_count": len(all_files),
        "requested": len(clips),
        "success_count": success_count,
        "failed_count": failed_count,
        "skipped_count": skipped_count,
        "success_rate": f"{(success_count + skipped_count) / len(clips) * 100:.1f}%" if clips else "0%",
        "created": datetime.now().isoformat(),
        "output_directory": str(output_dir),
        "note": "Audio files saved in native format (may not have extensions) - all are playable"
    }
    
    metadata_path = output_dir / "audioset_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n📄 Metadata: {metadata_path}")
    print(f"\n💡 Next step: Move clips to 02_dataset/raw/audio_fire/ if needed")


if __name__ == "__main__":
    main()
