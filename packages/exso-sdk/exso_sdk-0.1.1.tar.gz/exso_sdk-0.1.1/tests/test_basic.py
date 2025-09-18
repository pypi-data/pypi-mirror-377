import pandas as pd
from exso_sdk.preprocessing import clean_missing, normalize_scale
from exso_sdk.model import load_model, predict
from exso_sdk.config import REQUIRED_COLUMNS

def predict_single_sample(sample):
    # Convert sample dict to DataFrame with one row
    df = pd.DataFrame([sample])
    
    # Clean missing values (if any)
    df_clean = clean_missing(df, strategy='fill')
    
    # Normalize features
    features = REQUIRED_COLUMNS
    df_scaled, scaler = normalize_scale(df_clean, features)
    
    # Load model
    model = load_model(input_dim=len(features))
    
    # Extract feature vector as numpy array
    feature_vector = df_scaled.loc[0, features].values
    
    # Predict
    pred_class, probs = predict(model, feature_vector)
    label_map = {0: 'False Positive', 1: 'Candidate', 2: 'Positive'}
    pred_label = label_map.get(pred_class, str(pred_class))
    print(f"Predicted class: {pred_class} ({pred_label})")
    print(f"Probabilities: {probs}")

if __name__ == '__main__':
    sample = {
        'koi_period': 10.5,
        'koi_time0bk': 134.2,
        'koi_duration': 4.1,
        'koi_depth': 250.0,
        'koi_prad': 1.2,
        'koi_sma': 0.05,
        'koi_incl': 89.5,
        'koi_teq': 500,
        'koi_insol': 50,
        'koi_srho': 1.1,
        'koi_srad': 1.0,
        'koi_smass': 1.0,
        'koi_steff': 5700,
        'koi_slogg': 4.4,
        'koi_smet': 0.0,
        'koi_model_snr': 20.0
    }
    predict_single_sample(sample)
