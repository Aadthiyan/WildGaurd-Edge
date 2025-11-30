## EmberSense Raw Data Layout

All unprocessed assets live under `data/raw` and are subdivided by modality. Only metadata files are tracked in git; download instructions point to the original licensed sources.

### Directory map
- `data/raw/audio/wildfire_acoustic/` — positive-class cues (campfire crackle, brush ignition, low-intensity wildfire recordings) curated from AudioSet and vetted open corpora.
- `data/raw/audio/negative_events/` — confounding background (wind, rain, fauna, vehicles, human chatter) pulled from UrbanSound8K and other licensed field captures.
- `data/raw/sensors/environmental/` — temperature, humidity, VOC, and barometric traces derived from NASA Earthdata + NOAA surface networks; also hosts synthetic augmentations (sensor drift, noise injections).

Each leaf directory stores:
1. `README.source.md` — provenance, download commands, preprocessing directives.
2. `LICENSE.<source>.md` — verbatim license text from the provider.
3. Raw files organized by `source/<split>/<recording_id>`.

### Reproducible ingestion workflow
1. Run `python scripts/datasets/pull_audio.py --source audioset` (to be implemented) to fetch labeled CSVs and download clips via YouTube-DL-compatible mirrors that satisfy license requirements.
2. Run `python scripts/datasets/pull_sensors.py --source nasa_earthdata` to download environmental traces via their API using an .env-stored token.
3. Execute `python scripts/validators/validate_dataset_completeness.py --manifest metadata/dataset_manifest.json` to confirm counts and metadata coverage.
4. Log every transformation in `metadata/preprocessing_log.csv` (created in Week 1 Task 3) to maintain dataset lineage.

### Storage & versioning rules
- No proprietary or unlicensed data may enter `data/raw`.
- Large binaries stay out of git; use git-lfs or remote object storage and keep signed URLs + checksums in the manifest.
- Maintain deterministic train/val/test splits using seeded scripts under `scripts/splits/`.
- Any regenerated dataset must pass the validators before model training begins.

