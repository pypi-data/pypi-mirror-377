import os
import pandas as pd
import requests
from io import StringIO
from .config import REQUIRED_COLUMNS

def fetch_datasets():
    """
    Download Kepler/K2/TESS datasets from public URLs (example URLs).
    Returns list of DataFrames.
    """
    urls = {
        'kepler': 'https://example.com/kepler.csv',
        'k2': 'https://example.com/k2.csv',
        'tess': 'https://example.com/tess.csv',
    }
    dfs = []
    for name, url in urls.items():
        print(f"Fetching {name} dataset...")
        r = requests.get(url)
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text))
        dfs.append(df)
    return dfs

def load_csv(path):
    """
    Load dataset CSV into DataFrame.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    df = pd.read_csv(path)
    return df

def validate_dataset(df):
    """
    Check for required columns, types, and sensible ranges.
    Returns True if valid, else raises ValueError.
    """
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Example type checks
    for col in REQUIRED_COLUMNS:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise TypeError(f"Column {col} must be numeric")

    # Example range checks (simplified)
    if (df['koi_period'] <= 0).any():
        raise ValueError("koi_period must be positive")

    return True

def merge_datasets(list_of_dfs):
    """
    Combine multiple mission datasets, align columns.
    """
    # Keep only required columns and concatenate
    aligned_dfs = []
    for df in list_of_dfs:
        aligned_dfs.append(df[REQUIRED_COLUMNS].copy())
    merged = pd.concat(aligned_dfs, ignore_index=True)
    return merged

def split_train_val_test(df, ratios=(0.7, 0.15, 0.15), random_state=42):
    """
    Split DataFrame into train, val, test sets reproducibly.
    """
    from sklearn.model_selection import train_test_split
    train_ratio, val_ratio, test_ratio = ratios
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
        raise ValueError("Ratios must sum to 1")

    train_df, temp_df = train_test_split(df, test_size=(1 - train_ratio), random_state=random_state)
    val_size = val_ratio / (val_ratio + test_ratio)
    val_df, test_df = train_test_split(temp_df, test_size=(1 - val_size), random_state=random_state)
    return train_df, val_df, test_df
