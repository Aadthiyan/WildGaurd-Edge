## Week 1 Task 2 — Dataset Research, Collection & Licensing

### 1. Description
Curate multi-modal wildfire indicators by combining licensed acoustic corpora (AudioSet wildfire subset, UrbanSound8K confounders) with environmental sensor traces (NASA / NOAA). Ensure traceable ingestion, enforce licensing compliance, and prepare raw folders for deterministic pipelines.

### 2. Deliverables & Status
- **Curated raw dataset folder** ✅ — `data/raw/` directory tree with modality-specific subfolders, README, and `.gitkeep` placeholders ready for ingestion.
- **Licensing documentation** ✅ — `docs/licenses/dataset_licenses.md` capturing license terms, obligations, and workflow.

### 3. Dependencies
- **AudioSet**: wildfire-related audio (Fire, Crackle, Branch breaking). Requires ontology filtering and clip download via YouTube URLs with CC BY-friendly licenses.
- **UrbanSound8K**: negative/confounding urban/environmental sounds for robustness to false positives.
- **Sensor datasets**: NASA Earthdata + NOAA surface networks (temperature, humidity, VOC, pressure). API tokens managed via `.env`.

### 4. Collection Plan
1. **AudioSet subset**
   - Use ontology IDs 528 (Fire), 520 (Crackle), 503 (Branch breaking).
   - Download 10-second clips, resample to 16 kHz mono, store FLAC.
   - Annotate metadata in `metadata/audioset_catalog.csv`.
2. **UrbanSound8K negatives**
   - Extract original folds; map to EmberSense negative taxonomy.
   - Normalize sample rate to 16 kHz mono.
   - Maintain fold integrity for train/val/test.
3. **Environmental sensors**
   - Query NASA/NOAA for historically hot/dry regions during fire seasons.
   - Interpolate 1 Hz cadence, engineer Δ features at preprocessing stage.
   - Save as Parquet with schema versioning.

### 5. Licensing & Compliance
- Every source’s verbatim license text stored under `docs/licenses/text/`.
- Manifest fields include `license`, `url`, `checksum`, `attribution`.
- License verification script cross-checks manifest entries before data sync.

### 6. Tests
- **Dataset completeness validator**: `python scripts/validators/validate_dataset_completeness.py --manifest metadata/dataset_manifest.json`
- **License verification script**: `python scripts/validators/check_dataset_licenses.py --manifest metadata/dataset_manifest.json --registry docs/licenses/dataset_licenses.md`

Outputs of these tests (JSON summaries) must be archived in `artifacts/week1/`.

