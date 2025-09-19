import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler

def clean_missing(df, strategy='drop'):
    """
    Handle missing values.
    strategy: 'drop' or 'fill'
    """
    if strategy == 'drop':
        return df.dropna()
    elif strategy == 'fill':
        # Fill numeric columns with median
        for col in df.select_dtypes(include='number').columns:
            median = df[col].median()
            df[col] = df[col].fillna(median)
        # For categorical, fill with mode (if any)
        for col in df.select_dtypes(include='object').columns:
            mode = df[col].mode()[0]
            df[col] = df[col].fillna(mode)
        return df
    else:
        raise ValueError("strategy must be 'drop' or 'fill'")

def normalize_scale(df, cols, method='standard'):
    """
    Scale numeric features.
    method: 'standard' (z-score) or 'minmax'
    Returns scaled DataFrame and scaler object.
    """
    if method == 'standard':
        scaler = StandardScaler()
    elif method == 'minmax':
        scaler = MinMaxScaler()
    else:
        raise ValueError("method must be 'standard' or 'minmax'")

    df_scaled = df.copy()
    df_scaled[cols] = scaler.fit_transform(df[cols])
    return df_scaled, scaler

def encode_categorical(df):
    """
    One-hot encode categorical columns.
    """
    cat_cols = df.select_dtypes(include='object').columns
    if len(cat_cols) == 0:
        return df
    return pd.get_dummies(df, columns=cat_cols)

def preprocess_lightcurve(lc):
    """
    Placeholder for lightcurve preprocessing: detrend + resample.
    lc: pandas DataFrame with time and flux columns.
    """
    # Example: simple rolling median detrend
    lc = lc.copy()
    lc['flux_detrended'] = lc['flux'] / lc['flux'].rolling(window=101, center=True, min_periods=1).median()
    # Resample to fixed cadence (e.g., 30 min)
    lc_resampled = lc.set_index('time').resample('30T').mean().interpolate()
    return lc_resampled.reset_index()
