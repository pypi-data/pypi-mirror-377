import numpy as np
import pandas as pd

def compute_period_features(df):
    """
    Compute period harmonics and folded stats.
    """
    df = df.copy()
    df['period_harmonic_2'] = df['koi_period'] * 2
    df['period_harmonic_0.5'] = df['koi_period'] * 0.5
    # Example folded stats placeholder
    df['folded_mean'] = df['koi_depth'] / df['koi_duration']
    return df

def compute_statistical_features(df):
    """
    Compute mean, std, skew, kurtosis of numeric columns.
    """
    from scipy.stats import skew, kurtosis
    df = df.copy()
    numeric_cols = df.select_dtypes(include=np.number).columns
    for col in numeric_cols:
        df[f'{col}_skew'] = skew(df[col])
        df[f'{col}_kurtosis'] = kurtosis(df[col])
    return df

def compute_domain_features(df):
    """
    Compute domain-specific features like SNR, vetting flags.
    """
    df = df.copy()
    df['transit_snr'] = df['koi_depth'] / (df['koi_duration'] + 1e-6)
    # Example vetting flag: depth > threshold
    df['vet_flag'] = (df['koi_depth'] > 500).astype(int)
    return df