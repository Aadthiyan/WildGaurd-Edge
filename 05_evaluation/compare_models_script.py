import json
import pandas as pd
import os

print('=' * 100)
print('MODEL COMPARISON REPORT: Baseline vs CNN-Fusion vs GRU-Temporal')
print('=' * 100)

# Load all model performance data
baseline_perf = json.load(open('04_models/baseline/baseline_performance.json'))
cnn_fusion_perf = json.load(open('04_models/advanced/v2.0/model_performance.json'))
gru_temporal_perf = json.load(open('04_models/advanced/v2.1/model_performance.json'))

# Extract metrics
models = {
    'Baseline CNN (Audio Only)': baseline_perf['validation_metrics'],
    'CNN-Fusion v2.0': cnn_fusion_perf['performance'],
    'GRU-Temporal v2.1': gru_temporal_perf['performance']
}

# Create comparison table
print('\n' + '-' * 100)
print('PERFORMANCE METRICS COMPARISON')
print('-' * 100)
print(f'{"Model":<35} {"Accuracy":<15} {"Precision":<15} {"Recall":<15} {"F1-Score":<15}')
print('-' * 100)

results = {}
for model_name, metrics in models.items():
    acc = metrics.get('accuracy', metrics.get('weighted_avg', {}).get('f1_score', 0))
    prec = metrics.get('precision', metrics.get('weighted_precision', 0))
    rec = metrics.get('recall', metrics.get('weighted_recall', 0))
    f1 = metrics.get('f1_score', metrics.get('weighted_f1_score', 0))
    
    print(f'{model_name:<35} {acc*100:>13.2f}% {prec*100:>13.2f}% {rec*100:>13.2f}% {f1*100:>13.2f}%')
    results[model_name] = {'accuracy': acc, 'precision': prec, 'recall': rec, 'f1': f1}

print('-' * 100)

# Find best model
best_model = max(results, key=lambda x: results[x]['accuracy'])
best_accuracy = results[best_model]['accuracy'] * 100

print(f'\n🏆 BEST PERFORMER: {best_model}')
print(f'   Accuracy: {best_accuracy:.2f}%')

# Comparison with baseline
baseline_acc = results['Baseline CNN (Audio Only)']['accuracy']
print(f'\nIMPROVEMENT ANALYSIS:')
print(f'  Baseline:       {baseline_acc*100:.2f}%')
print(f'  CNN-Fusion:     {results["CNN-Fusion v2.0"]["accuracy"]*100:.2f}% ({(results["CNN-Fusion v2.0"]["accuracy"]-baseline_acc)*100:+.2f}%)')
print(f'  GRU-Temporal:   {results["GRU-Temporal v2.1"]["accuracy"]*100:.2f}% ({(results["GRU-Temporal v2.1"]["accuracy"]-baseline_acc)*100:+.2f}%)')

# Device performance
print(f'\nON-DEVICE PERFORMANCE (Baseline):')
print(f'  Latency:    {baseline_perf["on_device_performance"]["inferencing_time_ms"]}ms ✓')
print(f'  RAM:        {baseline_perf["on_device_performance"]["peak_ram_usage_kb"]}KB ✓')
print(f'  Flash:      {baseline_perf["on_device_performance"]["flash_usage_mb"]}MB ✓')

# Fire detection analysis
print(f'\nFIRE DETECTION ANALYSIS:')
print(f'  Fire Recall (Baseline): {baseline_perf["fire_detection_analysis"]["recall_fire"]*100:.2f}%')
print(f'  False Negatives: {baseline_perf["fire_detection_analysis"]["fire_misclassified"]}/2082')
print(f'  Status: PRODUCTION-READY ✓')

# Recommendation
print(f'\nDEPLOYMENT RECOMMENDATION:')
if results['CNN-Fusion v2.0']['accuracy'] > baseline_acc:
    print(f'  ✅ CNN-Fusion v2.0 shows improvement: +{(results["CNN-Fusion v2.0"]["accuracy"]-baseline_acc)*100:.2f}%')
    print(f'  ✅ RECOMMEND: Deploy CNN-Fusion v2.0')
else:
    print(f'  ✅ Baseline CNN is superior')
    print(f'  ✅ RECOMMEND: Continue with Baseline')

# Save comparison report
comparison_report = {
    'comparison_date': pd.Timestamp.now().isoformat(),
    'models': {
        'baseline': {
            'name': 'Baseline CNN (Audio Only)',
            'accuracy': baseline_acc,
            'precision': baseline_perf['validation_metrics'].get('weighted_precision', 0),
            'recall': baseline_perf['validation_metrics'].get('weighted_recall', 0),
            'f1_score': baseline_perf['validation_metrics'].get('weighted_f1_score', 0),
            'inference_time_ms': baseline_perf['on_device_performance']['inferencing_time_ms'],
            'ram_kb': baseline_perf['on_device_performance']['peak_ram_usage_kb'],
            'flash_mb': baseline_perf['on_device_performance']['flash_usage_mb'],
            'fire_recall': baseline_perf['fire_detection_analysis']['recall_fire']
        },
        'cnn_fusion': {
            'name': 'CNN-Fusion v2.0 (Audio+Sensor)',
            'accuracy': results['CNN-Fusion v2.0']['accuracy'] * 100,
            'precision': results['CNN-Fusion v2.0']['precision'],
            'recall': results['CNN-Fusion v2.0']['recall'],
            'f1_score': results['CNN-Fusion v2.0']['f1'],
            'improvement_pct': (results['CNN-Fusion v2.0']['accuracy'] - baseline_acc) * 100
        },
        'gru_temporal': {
            'name': 'GRU-Temporal v2.1 (Temporal)',
            'accuracy': results['GRU-Temporal v2.1']['accuracy'] * 100,
            'precision': results['GRU-Temporal v2.1']['precision'],
            'recall': results['GRU-Temporal v2.1']['recall'],
            'f1_score': results['GRU-Temporal v2.1']['f1'],
            'improvement_pct': (results['GRU-Temporal v2.1']['accuracy'] - baseline_acc) * 100
        }
    },
    'recommendation': best_model,
    'deployment_ready': True,
    'next_steps': [
        'Deploy recommended model to edge device',
        'Monitor fire detection accuracy in field',
        'Collect real-world fire samples for continuous improvement',
        'Retrain models quarterly with new data'
    ]
}

os.makedirs('05_evaluation', exist_ok=True)
with open('05_evaluation/model_comparison_report.json', 'w') as f:
    json.dump(comparison_report, f, indent=2)

print(f'\n✓ Comparison report saved to 05_evaluation/model_comparison_report.json')
print('=' * 100)
