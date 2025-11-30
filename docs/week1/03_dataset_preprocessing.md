## Week 1 Task 3 — Dataset Annotation, Preprocessing & Documentation

### 1. Description
Label wildfire-relevant audio events and environmental sensor segments, normalize duration/rate, and codify a deterministic preprocessing pipeline (scripts + notebook) that outputs ready-to-train datasets and documented splits.

### 2. Deliverables & Status
- **Annotated label files** ✅ — `metadata/labels/audio_event_annotations.csv` & `metadata/labels/sensor_segment_annotations.csv` provide schema-compliant annotations with example entries.
- **Preprocessing Jupyter notebook** ✅ — `notebooks/week1/embersense_preprocessing.ipynb` orchestrates audio cleanup, sensor normalization, feature caching, and split serialization.
- **Dataset summary report** ✅ — This document + generated summaries in `artifacts/week1/dataset_summary.json`.

### 3. Dependencies
- Python 3.11, pandas, numpy, librosa, scipy, soundfile, pyarrow.
- Edge Impulse DSP blocks (referenced when exporting features).
- Raw data + manifest from Tasks 1–2.

### 4. Annotation Workflow
1. Import candidate metadata from AudioSet ontology filter + UrbanSound8K CSV.
2. Use the notebook’s `annotate_audio_event` helper to visualize spectrograms and capture label spans.
3. Append validated rows to `metadata/labels/audio_event_annotations.csv`; record reviewer ID in `annotator` column.
4. For environmental traces, tag 30-minute windows as `pre_fire_alert` vs `nominal` using humidity/VOC heuristics; store in `sensor_segment_annotations.csv`.

### 5. Preprocessing Pipeline Overview
1. **Audio normalization**
   - Resample to 16 kHz mono.
   - Trim/loop to fixed 10 s with fade edges.
   - Apply -20 dB LUFS normalization and band-pass (300–8000 Hz).
   - Export cleaned FLAC + feature-ready numpy arrays.
2. **Sensor processing**
   - Interpolate to 1 Hz cadence, fill gaps ≤60 s via linear method.
   - Z-score per channel within each station.
   - Derive Δ features (first difference, rolling std).
3. **Splits**
   - Stratified by label/source with seed 42.
   - Persist to `metadata/splits/dataset_splits.json`.
4. **Logging & artifacts**
   - Every step logged in `metadata/preprocessing_log.csv`.
   - Executed notebook saved under `artifacts/week1/`.

### 6. Tests
- **Label consistency tests**: `python scripts/validators/check_label_consistency.py --report artifacts/week1/label_consistency.json`
- **Pipeline reproduction**: `python scripts/preprocessing/run_preprocessing.py --executed-notebook artifacts/week1/embersense_preprocessing.executed.ipynb`

Passing both tests + archived artifact JSON constitutes acceptance for Task 3.

