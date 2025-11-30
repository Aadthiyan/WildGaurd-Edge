# EmberSense Quick Start Guide

## What You Need to Provide

### 1. Edge Impulse Credentials
- **API Key**: Get from https://studio.edgeimpulse.com/ → Profile → API Keys
- **Project ID**: Get from your Edge Impulse project URL or settings

### 2. Dataset Files (Optional - if you have them)
- Audio files: `02_dataset/raw/audio_fire/` and `02_dataset/raw/audio_non_fire/`
- Sensor data: `02_dataset/raw/sensor_fire/` (Parquet files)

## Setup Steps

### Step 1: Install Dependencies
```bash
# Install Edge Impulse CLI
npm install -g edge-impulse-cli

# Install Python dependencies (if requirements.txt exists)
pip install -r requirements.txt
```

### Step 2: Configure Credentials
```bash
# Run setup script
python scripts/setup_edge_impulse.py

# Or manually create .env file:
# EI_API_KEY=your_key_here
# EI_PROJECT_ID=your_project_id_here
```

### Step 3: Login to Edge Impulse
```bash
edge-impulse-cli login
# Enter your API key when prompted
```

## What to Do in Edge Impulse Studio

### 1. Create Project
1. Go to https://studio.edgeimpulse.com/
2. Click "Create new project"
3. Name: "EmberSense"
4. Select: "Audio + Environmental sensors"
5. Copy Project ID

### 2. Upload Data
1. **Audio Data**:
   - Go to "Data Acquisition" → "Upload data"
   - Upload fire samples → Label as "fire", "crackle", etc.
   - Upload negative samples → Label as "rain", "wind", etc.
   - Click "Perform train/test split"

2. **Sensor Data**:
   - Go to "Data Acquisition" → "Upload data"
   - Select "Time series"
   - Upload Parquet files
   - Configure channels: temperature, humidity, VOC, pressure
   - Label segments: "pre_fire_alert" or "nominal"

### 3. Configure DSP Pipeline
1. Go to "Impulse Design" → "Create Impulse"
2. Add inputs:
   - "Time series (audio)" @ 16 kHz, 10s
   - "Time series (other)" @ 1 Hz, 30s
3. Add processing blocks:
   - Audio (MFE) - use config from `03_feature_pipeline/edge_impulse/project_export.json`
   - MFCC (13 coefficients + deltas)
   - Spectrogram
   - Sensor Fusion (mean/std/min/max/slope)
4. Click "Save Impulse"
5. Click "Generate Features"

### 4. Train Models
1. Go to "Impulse Design" → "Learning Block"
2. Add "Classification (Keras)"
3. Configure architecture
4. Click "Start Training"
5. Export model and metrics

### 5. Optimize Model
1. Go to "Deployment" → "Optimize model"
2. Select "INT8 quantization"
3. Target: Cortex-M4F @ 80MHz
4. Click "Optimize"
5. Run profiler to check latency and size

## Running Our Scripts

Once Edge Impulse is set up, our scripts will:
- Automatically connect using your credentials
- Train models via CLI
- Download results
- Compare performance
- Generate reports

### Example Commands
```bash
# Train advanced model
python 04_models/advanced/train_advanced.py \
    --config 04_models/advanced/configs/cnn_fusion_v2.json \
    --experiment-name exp_001 \
    --version v2.0 \
    --edge-impulse-project-id $EI_PROJECT_ID

# Quantize model
python 04_models/optimized/quantize_model.py \
    --input-model 04_models/advanced/versions/v2.0/model.h5 \
    --output-dir 04_models/optimized/quantized/v2.0_int8 \
    --edge-impulse-project-id $EI_PROJECT_ID

# Benchmark
python 04_models/optimized/benchmark_simulation.py \
    --model 04_models/optimized/quantized/v2.0_int8/model.eim \
    --output 04_models/optimized/benchmarks/v2.0_int8_benchmark.json
```

## Summary Checklist

- [ ] Create Edge Impulse account
- [ ] Get API key
- [ ] Create project "EmberSense"
- [ ] Get Project ID
- [ ] Run `python scripts/setup_edge_impulse.py`
- [ ] Edit `.env` with credentials
- [ ] Login: `edge-impulse-cli login`
- [ ] Upload data to Edge Impulse Studio
- [ ] Configure DSP pipeline
- [ ] Train models
- [ ] Run our scripts with your Project ID

## Need Help?

- See `docs/EDGE_IMPULSE_SETUP.md` for detailed instructions
- Edge Impulse Docs: https://docs.edgeimpulse.com/
- Edge Impulse Forum: https://forum.edgeimpulse.com/

