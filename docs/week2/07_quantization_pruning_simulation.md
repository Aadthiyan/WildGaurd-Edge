# Task 7 – Quantization, Pruning & Edge Deployment Simulation

## Description
Optimize models (quantization/pruning) for MCU-grade performance without involving real hardware. All optimization and benchmarking is performed using Edge Impulse simulation tools.

## Deliverables

### 1. Quantized Model ✅
- **Location**: `04_models/optimized/quantized/`
- **Format**: INT8 quantized models (`.eim` or `.tflite`)
- **Methods**:
  - Post-training INT8 quantization
  - Quantization-aware training (optional)
  - Dynamic range quantization

### 2. Pruned Model ✅
- **Location**: `04_models/optimized/pruned/`
- **Format**: Pruned H5 models
- **Methods**:
  - Magnitude-based pruning
  - Structured pruning
  - Iterative pruning with fine-tuning

### 3. Simulation Benchmarks ✅
- **Location**: `04_models/optimized/benchmarks/`
- **Format**: JSON benchmark results + Markdown reports
- **Metrics**:
  - Latency (ms)
  - Flash size (KB)
  - RAM usage (KB)
  - Total memory (KB)
  - Inference cycles

## Dependencies
- **Edge Impulse deployment tools**: Primary optimization and simulation platform
- **TensorFlow Model Optimization Toolkit**: For pruning
- **TensorFlow Lite**: Alternative quantization tool
- **Optimized models**: From Task 6 (advanced models)

## Optimization Targets
- **Latency**: < 50ms (simulated on Cortex-M4F @ 80MHz)
- **Model Size**: < 300KB total (Flash + RAM)
- **Accuracy**: Maintain ≥85% (max 2% degradation)

## Usage

### Quantize a Model
```bash
python 04_models/optimized/quantize_model.py \
    --input-model 04_models/advanced/versions/v2.0/model.h5 \
    --output-dir 04_models/optimized/quantized/v2.0_int8 \
    --method int8 \
    --tool edge_impulse \
    --edge-impulse-project-id <PROJECT_ID>
```

### Prune a Model
```bash
python 04_models/optimized/prune_model.py \
    --input-model 04_models/advanced/versions/v2.0/model.h5 \
    --output-dir 04_models/optimized/pruned/v2.0_pruned \
    --sparsity 0.5 \
    --method magnitude
```

### Run Simulation Benchmark
```bash
python 04_models/optimized/benchmark_simulation.py \
    --model 04_models/optimized/quantized/v2.0_int8/model.eim \
    --target-mcu cortex-m4f \
    --frequency 80 \
    --output 04_models/optimized/benchmarks/v2.0_int8_benchmark.json \
    --report 04_models/optimized/benchmarks/v2.0_int8_benchmark.md
```

### Complete Optimization Pipeline
```bash
python 04_models/optimized/optimize_pipeline.py \
    --input-model 04_models/advanced/versions/v2.0/model.h5 \
    --output-prefix v2.0_optimized \
    --quantize \
    --prune \
    --benchmark
```

## Tests

### Latency Test
- **Requirement**: Inference latency < 50ms
- **Method**: Edge Impulse simulation on Cortex-M4F @ 80MHz
- **Command**: `benchmark_simulation.py` validates against target

### Model Size Test
- **Requirement**: Model size < 300KB (Flash + RAM)
- **Method**: File size calculation + Edge Impulse profiler
- **Command**: `benchmark_simulation.py` validates against target

### Accuracy Preservation Test
- **Requirement**: Accuracy drop < 2% from original
- **Method**: Compare quantized/pruned model accuracy vs. original
- **Validation**: Manual comparison of evaluation metrics

### Test Command
```bash
# Run full optimization and validation
python 04_models/optimized/optimize_pipeline.py \
    --input-model 04_models/advanced/versions/v2.0/model.h5 \
    --output-prefix v2.0_optimized \
    --quantize \
    --prune \
    --benchmark

# Check results
python 04_models/optimized/benchmark_simulation.py \
    --model 04_models/optimized/quantized/v2.0_optimized_int8/model.eim \
    --output 04_models/optimized/benchmarks/v2.0_optimized_benchmark.json \
    --targets 04_models/optimized/configs/simulation_targets.json
```

## Optimization Workflow

1. **Start with advanced model** (from Task 6)
2. **Quantize** to INT8 using Edge Impulse
3. **Prune** to reduce model size (optional)
4. **Benchmark** using Edge Impulse simulation
5. **Validate** against targets (latency <50ms, size <300KB)
6. **Compare** accuracy vs. original model

## Configuration Files

- `configs/quantization_config.json` - Quantization settings
- `configs/pruning_config.json` - Pruning settings
- `configs/simulation_targets.json` - Target metrics and MCU configs

## Status
- ✅ Quantization framework
- ✅ Pruning framework
- ✅ Simulation benchmarking
- ✅ Optimization pipeline
- ⏳ Actual optimization runs (pending Edge Impulse API key)
- ⏳ Benchmark validation

