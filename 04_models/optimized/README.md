# Model Optimization & Edge Deployment Simulation

This directory contains quantized, pruned, and optimized models for MCU deployment, along with simulation benchmarks.

## Structure
- `quantized/` - INT8 quantized model variants
- `pruned/` - Pruned model variants
- `simulations/` - Edge Impulse simulation results
- `benchmarks/` - Performance benchmark reports
- `configs/` - Optimization configuration files

## Optimization Targets
- **Latency**: < 50ms (simulated on Cortex-M4F @ 80MHz)
- **Model Size**: < 300KB total (Flash + RAM)
- **Accuracy**: Maintain ≥85% (minimal degradation)

## Optimization Methods

### Quantization
- INT8 quantization via Edge Impulse
- Post-training quantization
- Quantization-aware training (optional)

### Pruning
- Magnitude-based pruning
- Structured pruning
- Iterative pruning with fine-tuning

## Usage

### Quantize a Model
```bash
python 04_models/optimized/quantize_model.py \
    --input-model 04_models/advanced/versions/v2.0/model.h5 \
    --output-dir 04_models/optimized/quantized/v2.0_int8 \
    --method int8
```

### Prune a Model
```bash
python 04_models/optimized/prune_model.py \
    --input-model 04_models/advanced/versions/v2.0/model.h5 \
    --output-dir 04_models/optimized/pruned/v2.0_pruned \
    --sparsity 0.5
```

### Run Simulation Benchmark
```bash
python 04_models/optimized/benchmark_simulation.py \
    --model 04_models/optimized/quantized/v2.0_int8/model.eim \
    --target-mcu cortex-m4f \
    --output 04_models/optimized/benchmarks/v2.0_int8_benchmark.json
```

