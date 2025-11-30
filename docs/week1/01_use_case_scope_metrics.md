## EmberSense Use Case, Scope, and Metrics

### 1. Problem Statement
- **Wildfire risk**: Acoustic signatures (branch crackle, combustion pops) and abrupt environmental shifts (temperature spikes, humidity drops, VOC sensor spikes) precede visible flames by minutes.
- **Operational gap**: Remote forest deployments lack continuous human monitoring; satellite cues arrive too late for sub-50 min response targets.
- **Goal**: Build EmberSense, an MCU-friendly, multi-modal detection system that fuses audio and ambient sensors to flag early-stage wildfire indicators in under 50 ms simulated latency with ≥ 85 % event-level accuracy.

### 2. Objectives
- **Dataset pipeline**: Curate/licensed acoustic wildfire cues (campfire crackle, brush ignition, wind/animal confounders) plus open environmental sensor traces (temperature, humidity, VOC, barometric pressure). Enforce deterministic splits and augmentation logs.
- **DSP stack**: Derive 64-bin log-Mel spectrograms + 13-coefficient MFCCs for audio; compute rolling means/variance, Δ features, and normalized gradients for environmental channels.
- **Modeling**: Establish a classical baseline (logistic regression / Gaussian NB) followed by a compact CNN+GRU fusion model within 300 KB memory, trained/exported via Edge Impulse.
- **Simulation**: Validate latency (<50 ms), RAM, and Flash usage using Edge Impulse’s MCU profiler; document quantization/pruning experiments (INT8, DS-CNN depthwise variants) performed only in simulation.
- **Documentation & governance**: Maintain reproducible notebooks/logs, license manifests, and an audit-ready README for hackathon submission.

### 3. Success Metrics
- **Accuracy**: ≥ 85 % macro F1 and event-level accuracy on held-out validation segments.
- **Latency**: < 50 ms inference time in Edge Impulse simulator for target MCU class (Cortex-M4F @ 80 MHz).
- **Memory footprint**: < 300 KB total (Flash + RAM) for the deployed model bundle.
- **Data integrity**: 100 % traceable preprocessing lineage; zero label leakage across train/val/test.

### 4. Scope & Assumptions
- **Sensing modalities**: Single-channel MEMS microphone (16 kHz max), plus low-rate environmental sensors (1–5 Hz for temp/humidity/VOC/barometer). Data collected/simulated under diverse forest biomes.
- **Operational context**: Stationary nodes, solar-backed, no cellular guarantee—focus on on-device inference with periodic LoRa uplinks.
- **Threat classes**: Early combustion (campfire-to-wildfire transition), human-made noise (vehicles, chainsaws), benign nature sounds (rain, wind, fauna) treated as negative class.
- **Assumptions**:
  - All datasets carry permissive licenses (CC BY, CC0, NASA open data) verified before ingestion.
  - Sensor noise and calibration drift modeled synthetically; no real hardware required.
  - Edge Impulse Studio acts as the single source of truth for DSP pipelines, model versions, and simulated deployment metrics.
  - Latency and memory numbers are simulator-derived; no physical MCU flashing.

### 5. Dependencies
- **Research inputs**:
  - National Interagency Fire Center incident after-action reports (acoustic cues & timelines).
  - USDA Forest Service “Early Detection of Wildfire Ignitions Using Acoustic Sensing” (2023) for spectral signatures.
  - NASA Earthdata open environmental sensor corpora (temperature/humidity baselines).
  - Edge Impulse Studio (DSP blocks, EON Tuner, MCU profiler).
- **Tooling**: Python 3.11 environment for preprocessing scripts, librosa/scipy for DSP prototyping, pandas for dataset manifests, Git for version control.

### 6. Tests — Peer-Review Checklist
1. **Traceability**: Does every dataset entry map to a license source and preprocessing log?
2. **Metric coverage**: Are accuracy, latency, memory targets explicitly tied to evaluation scripts and Edge Impulse profiles?
3. **Assumption validation**: Are sensing/operational assumptions documented and justified via references?
4. **Reproducibility**: Can another engineer recreate the dataset splits and DSP features from the documented pipeline without external knowledge?
5. **Risk review**: Are false-positive/false-negative impacts discussed, with mitigation strategies (e.g., multi-frame voting)?

Completion of this checklist by an independent reviewer constitutes acceptance for Week 1, Task 1.

