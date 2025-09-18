from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import traceback
from .model import load_model, predict
from .data import validate_dataset
from .preprocessing import clean_missing, normalize_scale, encode_categorical
from .config import REQUIRED_COLUMNS, MODEL_PATH

app = Flask(__name__)

# Load model on startup
input_features = REQUIRED_COLUMNS
model = load_model(input_dim=len(input_features))

@app.route('/')
def ui_render_home():
    return """
    <h1>Exoplanet Predictor</h1>
    <p>Upload CSV with required columns to predict exoplanet candidates.</p>
    <form action="/predict" method="post" enctype="multipart/form-data">
      <input type="file" name="file" />
      <input type="submit" value="Predict" />
    </form>
    """

@app.route('/predict', methods=['POST'])
def api_predict():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        df = pd.read_csv(file)
        validate_dataset(df)
        df = clean_missing(df, strategy='fill')
        # Normalize features
        df_scaled, _ = normalize_scale(df, input_features)
        preds = []
        probs_list = []
        for _, row in df_scaled.iterrows():
            pred_class, probs = predict(model, row[input_features].values)
            preds.append(pred_class)
            probs_list.append(probs.tolist())
        df['prediction'] = preds
        label_map = {0: 'False Positive', 1: 'Candidate', 2: 'Positive'}
        df['prediction_label'] = df['prediction'].map(label_map)
        # include probabilities
        results = []
        for i, row in df.iterrows():
            results.append({
                'prediction': int(row['prediction']),
                'prediction_label': row['prediction_label'],
                'probabilities': probs_list[i]
            })
        return jsonify({'results': results})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def main():
    app.run(host='0.0.0.0', port=5000, debug=True)