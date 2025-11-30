## Week 1 Task 4 — DSP & Feature Extraction Pipeline (Edge Impulse)

### 1. Description
Configure multi-branch audio + environmental DSP blocks in Edge Impulse Studio so EmberSense can ingest normalized clips and produce MFCC, log-Mel spectrogram, and sensor-fusion statistical features ready for MCU-focused modeling.

### 2. Deliverables & Status
- **DSP pipeline configured** ✅ — JSON snapshot (`edge_impulse/dsp_pipeline.json`) matches the Edge Impulse pipeline settings (Audio MFE → MFCC, Spectrogram, Sensor Fusion) with reproducible parameters.
- **Feature previews** ✅ — Example previews exported to `artifacts/week1/feature_previews/` (PNG + JSON summaries) after uploading seed samples to Edge Impulse.

### 3. Edge Impulse Configuration Steps
1. **Create Project**: Edge Impulse Studio → “EmberSense” → select “Audio + Environmental sensors” template.
2. **Upload Data**: Use normalized audio FLAC + sensor Parquet exports from Task 3 (via EI CLI or web uploader).
3. **Impulse Design**:
   - Input block: “Time series (audio)” @ 16 kHz, 10 s; add second input “Time series (other)” @ 1 Hz, 30 s.
   - Add DSP blocks:
     - `Audio (MFE)` with params in JSON (`window_length_ms=1000`, `mel_bands=64`, etc.).
     - `MFCC` block chained to MFE output (13 coefficients, Δ enabled).
     - `Spectrogram` block fed directly from raw audio stream (64 ms window, log magnitude).
     - `Spectral features (custom)` → configure as Sensor Fusion block for temp/humidity/VOC/pressure stats (mean/std/min/max/slope per 30 s window).
   - Output features: fuse MFCC + Spectrogram + Sensor features before feeding into the classifier block (to be built in Week 2).
4. **Save settings** and export a pipeline snapshot (Edge Impulse “Download block parameters”) to keep the JSON in version control.

### 4. Feature Previews
- After configuring, run Edge Impulse “Generate features” to create MFCC & spectrogram previews for representative samples (fire, rain, nominal sensor segment).
- Export PNGs & JSON histograms (Edge Impulse “Download sample features”) for traceability:
  - `artifacts/week1/feature_previews/mfcc_fire_sample.png`
  - `artifacts/week1/feature_previews/spectrogram_rain_sample.png`
  - `artifacts/week1/feature_previews/sensor_features_prefire.json`
- Use these previews during model reviews to confirm discriminative cues (e.g., low-frequency crackle energy, humidity slope).

### 5. Dependencies
- Edge Impulse Studio (web) + CLI (`edge-impulse-cli`) for uploading data and exporting DSP configurations.
- Python libs from Task 3 to produce normalized inputs.

### 6. Tests
- **Noise robustness test**: run `python scripts/dsp/noise_robustness_test.py --config edge_impulse/dsp_pipeline.json --snr-list 0 5 10` to inject Gaussian noise into audio samples and ensure MFCC variance remains within tolerance (<15% drift). Document output in `artifacts/week1/feature_previews/noise_robustness.json`.
- **Feature quality inspection**: `python scripts/dsp/feature_quality_report.py --sample EVT0001 --config edge_impulse/dsp_pipeline.json --out artifacts/week1/feature_previews/feature_quality_EVT0001.json` to validate energy coverage, spectral centroid, and sensor feature sanity vs. expected ranges.

Passing both tests and archiving artifacts constitutes acceptance for Task 4.

