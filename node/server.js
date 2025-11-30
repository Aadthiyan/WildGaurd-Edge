const express = require('express');
const cors = require('cors');
const fs = require('fs');

// Load the inferencing WebAssembly module
const Module = require('./edge-impulse-standalone');

const app = express();
app.use(cors());
app.use(express.json());

// Classifier module
let classifierInitialized = false;
Module.onRuntimeInitialized = function() {
    classifierInitialized = true;
    console.log('✅ Edge Impulse model loaded!');
};

class EdgeImpulseClassifier {
    _initialized = false;

    init() {
        if (classifierInitialized === true) return Promise.resolve();

        return new Promise((resolve, reject) => {
            Module.onRuntimeInitialized = () => {
                classifierInitialized = true;
                let ret = Module.init();
                if (typeof ret === 'number' && ret != 0) {
                    return reject('init() failed with code ' + ret);
                }
                resolve();
            };
        });
    }

    classify(rawData, debug = false) {
        if (!classifierInitialized) throw new Error('Module is not initialized');

        const obj = this._arrayToHeap(rawData);
        let ret = Module.run_classifier(obj.buffer.byteOffset, rawData.length, debug);
        Module._free(obj.ptr);

        if (ret.result !== 0) {
            throw new Error('Classification failed (err code: ' + ret.result + ')');
        }

        return this._fillResultStruct(ret);
    }

    _arrayToHeap(data) {
        let typedArray = new Float32Array(data);
        let numBytes = typedArray.length * typedArray.BYTES_PER_ELEMENT;
        let ptr = Module._malloc(numBytes);
        let heapBytes = new Uint8Array(Module.HEAPU8.buffer, ptr, numBytes);
        heapBytes.set(new Uint8Array(typedArray.buffer));
        return { ptr: ptr, buffer: heapBytes };
    }

    _fillResultStruct(ret) {
        let props = Module.get_properties();

        let jsResult = {
            anomaly: ret.anomaly,
            results: []
        };

        for (let cx = 0; cx < ret.size(); cx++) {
            let c = ret.get(cx);
            jsResult.results.push({ label: c.label, value: c.value });
            c.delete();
        }

        ret.delete();

        return jsResult;
    }
}

let classifier = new EdgeImpulseClassifier();

// Initialize classifier on startup
classifier.init().then(() => {
    console.log('✅ Edge Impulse Classifier initialized');
}).catch(err => {
    console.error('❌ Failed to initialize classifier:', err);
});

// POST /api/predict - accepts feature array
app.post('/api/predict', (req, res) => {
    try {
        const features = req.body.features;
        
        if (!features || !Array.isArray(features) || features.length === 0) {
            return res.status(400).json({ 
                status: 'error',
                message: 'Invalid features. Expected array of numbers.' 
            });
        }

        // Convert to numbers
        const numFeatures = features.map(f => parseFloat(f));

        // Classify
        const result = classifier.classify(numFeatures);
        
        // Find fire and non-fire predictions
        const fireResult = result.results.find(r => r.label === 'fire');
        const nominalResult = result.results.find(r => r.label === 'nominal');
        const rainResult = result.results.find(r => r.label === 'rain');
        const windResult = result.results.find(r => r.label === 'wind');

        const fireConfidence = fireResult ? fireResult.value : 0;
        
        res.json({
            status: 'success',
            prediction: fireConfidence > 0.5 ? 1 : 0,
            prediction_text: fireConfidence > 0.5 ? 'FIRE DETECTED 🔥' : 'NO FIRE ✅',
            confidence: fireConfidence,
            confidence_percent: (fireConfidence * 100).toFixed(1),
            all_results: result.results,
            model_type: 'Edge Impulse (98.92% accuracy)'
        });
    } catch (err) {
        console.error('Prediction error:', err);
        res.status(500).json({ 
            status: 'error',
            message: err.message
        });
    }
});

// GET /api/health - check if model is ready
app.get('/api/health', (req, res) => {
    res.json({ 
        status: classifierInitialized ? 'ready' : 'initializing',
        model: 'Edge Impulse Fire Detection',
        accuracy: '98.92%'
    });
});

// GET /api/model-info
app.get('/api/model-info', (req, res) => {
    res.json({
        status: 'success',
        model_name: 'Edge Impulse CNN',
        accuracy: 0.9892,
        fire_recall: 0.9976,
        latency_ms: 32,
        model_size_mb: 1.1,
        ready: classifierInitialized
    });
});

const PORT = 5001;
app.listen(PORT, () => {
    console.log('\n' + '='.repeat(80));
    console.log('🔥 Edge Impulse Model Server');
    console.log('='.repeat(80));
    console.log(`\n✅ Server running on http://localhost:${PORT}`);
    console.log('\nEndpoints:');
    console.log('  POST /api/predict       - Classify features (accepts JSON with "features" array)');
    console.log('  GET  /api/health        - Check if model is ready');
    console.log('  GET  /api/model-info    - Get model metrics');
    console.log('\nModel Info:');
    console.log('  Accuracy: 98.92%');
    console.log('  Fire Detection Recall: 99.76%');
    console.log('  Latency: 32ms');
    console.log('  Model Size: 1.1MB');
    console.log('\n' + '='.repeat(80) + '\n');
});
