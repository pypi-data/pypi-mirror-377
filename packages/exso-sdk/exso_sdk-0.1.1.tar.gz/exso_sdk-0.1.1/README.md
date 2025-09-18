## exso-sdk

Exoplanet candidate classification SDK (3-class). Provides data utilities, preprocessing, feature engineering, PyTorch model loading/prediction, simple gradient-based explanations, metrics, and a minimal Flask API.

- Classes: 0 = False Positive, 1 = Candidate, 2 = Positive

### Installation

```bash
pip install exso-sdk
```

Python 3.11+ is required.

### Model file

By default the SDK loads the model from an environment variable or the built-in default path:

- Set explicitly (recommended):
```bash
export EXSO_MODEL_PATH="/absolute/path/to/exoplanet_model.pth"
```

- Otherwise, it will look for `model/exoplanet_model.pth` placed next to your project root.

Your `.pth` can be either a raw `state_dict` or a checkpoint dict containing `model_state_dict`.

### Quickstart

```python
import numpy as np
import pandas as pd

from exso_sdk.config import REQUIRED_COLUMNS
from exso_sdk.preprocessing import clean_missing, normalize_scale
from exso_sdk.model import load_model, predict

# 1) Build a single-row DataFrame containing all required features
row = {
    'koi_period': 10.5, 'koi_time0bk': 134.2, 'koi_duration': 4.1, 'koi_depth': 250.0,
    'koi_prad': 1.2, 'koi_sma': 0.05, 'koi_incl': 89.5, 'koi_teq': 500, 'koi_insol': 50,
    'koi_srho': 1.1, 'koi_srad': 1.0, 'koi_smass': 1.0, 'koi_steff': 5700,
    'koi_slogg': 4.4, 'koi_smet': 0.0, 'koi_model_snr': 20.0
}
df = pd.DataFrame([row])

# 2) Clean & scale
df_clean = clean_missing(df, strategy='fill')
df_scaled, _ = normalize_scale(df_clean, REQUIRED_COLUMNS)
feature_vector = df_scaled.loc[0, REQUIRED_COLUMNS].values.astype(np.float32)

# 3) Load model and predict
model = load_model(input_dim=len(REQUIRED_COLUMNS))
pred_class, probs = predict(model, feature_vector)

label_map = {0: 'False Positive', 1: 'Candidate', 2: 'Positive'}
print('Predicted:', pred_class, label_map[pred_class])
print('Probabilities [0,1,2]:', probs)
```

### Explanations (saliency)

```python
from exso_sdk.explain import explain_prediction

saliency = explain_prediction(model, feature_vector, target_class_index=pred_class)
for name, score in zip(REQUIRED_COLUMNS, saliency):
    print(f"{name}: {float(score):.6f}")
```

### Data utilities

```python
from exso_sdk.data import load_csv, validate_dataset, merge_datasets, split_train_val_test

df = load_csv("/path/to/dataset.csv")
validate_dataset(df)  # raises if invalid

# Merge multiple DataFrames that contain REQUIRED_COLUMNS
merged = merge_datasets([df])
train_df, val_df, test_df = split_train_val_test(merged)
```

### Preprocessing

```python
from exso_sdk.preprocessing import clean_missing, normalize_scale, encode_categorical, preprocess_lightcurve

df_filled = clean_missing(df, strategy='fill')
df_scaled, scaler = normalize_scale(df_filled, REQUIRED_COLUMNS, method='standard')
df_encoded = encode_categorical(df_filled)

# Lightcurve placeholder utility (expects columns: time, flux)
# lc_processed = preprocess_lightcurve(lightcurve_df)
```

### Feature engineering

```python
from exso_sdk.features import compute_period_features, compute_statistical_features, compute_domain_features

df_feat = compute_period_features(df)
df_feat = compute_statistical_features(df_feat)
df_feat = compute_domain_features(df_feat)
```

### Training and evaluation (advanced)

These helpers assume you prepare `DataLoader`s that yield `(X_batch, y_batch)` where `y_batch` contains class indices {0,1,2}.

```python
from exso_sdk.model import build_model, train_model, evaluate_model
from torch.utils.data import TensorDataset, DataLoader
import torch

X = torch.tensor(df_scaled[REQUIRED_COLUMNS].values, dtype=torch.float32)
y = torch.randint(0, 3, (len(X),))  # placeholder labels for example
train_loader = DataLoader(TensorDataset(X, y), batch_size=32, shuffle=True)
val_loader = DataLoader(TensorDataset(X, y), batch_size=32)

model = build_model(input_dim=len(REQUIRED_COLUMNS))
train_model(model, train_loader, val_loader, config={"epochs": 2, "lr": 1e-3})
metrics = evaluate_model(model, val_loader)
print(metrics)
```

### REST API (Flask)

Expose a minimal upload-and-predict endpoint.

```bash
exso-sdk-api  # starts on http://0.0.0.0:5000/
```

POST `/predict` with a CSV file containing `REQUIRED_COLUMNS`. Response includes `prediction` (0/1/2), `prediction_label`, and `probabilities` per row.

### Error handling and utilities

```python
from exso_sdk.utils import log_metrics, handle_errors

log_metrics("run-123", {"accuracy": 0.9})
try:
    ...
except Exception as e:
    handle_errors(e)
```

### Versioning and compatibility

- Python: >= 3.11
- PyTorch: >= 1.7
- If you use a custom model, it must output 3 logits (shape `[batch, 3]`).


