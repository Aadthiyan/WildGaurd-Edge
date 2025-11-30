## EmberSense Dataset Licensing Register

| Dataset | License | Obligations | Notes |
| --- | --- | --- | --- |
| AudioSet (wildfire subset) | Creative Commons Attribution 4.0 (CC BY 4.0) | Cite Google AudioSet in documentation and UI; provide link to license; indicate any modifications. | Audio clips sourced via YouTube; ensure each uploader's license permits redistribution. Keep raw URLs + transcripts in `02_dataset/processed/source_log.csv`. |
| UrbanSound8K | Creative Commons Attribution 4.0 (CC BY 4.0) | Credit "UrbanSound8K by Salamon et al." in README; share derivative annotations under same CC BY terms. | Use only files with verified metadata; maintain original filename mapping for traceability. |
| NASA/NOAA environmental sensors | U.S. Government Public Domain (17 USC §105) | Attribute NASA Earthdata / NOAA even though not legally required; do not imply endorsement. | Follow Earthdata data-use policy; retain API request logs for audit. |

### Licensing workflow
1. Record each download event in `02_dataset/processed/source_log.csv` with fields: `source_id`, `timestamp`, `license`, `url`, `checksum`.
2. Store verbatim license text in `02_dataset/licensing/text/<source>.txt` (auto-populated by future scripts).
3. Run `python 02_dataset/scripts/check_dataset_licenses.py --manifest 02_dataset/raw/metadata_raw.json --registry 02_dataset/licensing/dataset_licenses.md` before distributing any derived dataset.

### Compliance checklist
- [ ] License texts synced with upstream (no stale versions).
- [ ] Attribution statements included in README + Edge Impulse project description.
- [ ] Redistribution boundaries documented (no commercial-only assets).
- [ ] External collaborators briefed on CC BY obligations.

