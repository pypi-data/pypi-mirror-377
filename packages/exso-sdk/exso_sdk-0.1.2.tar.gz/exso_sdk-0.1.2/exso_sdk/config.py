import os

# Resolve model path relative to this package directory by default
_PACKAGE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.environ.get(
    'EXSO_MODEL_PATH',
    os.path.join(os.path.dirname(_PACKAGE_DIR), 'model', 'exoplanet_model.pth')
)

REQUIRED_COLUMNS = [
    'koi_period', 'koi_time0bk', 'koi_duration', 'koi_depth', 'koi_prad',
    'koi_sma', 'koi_incl', 'koi_teq', 'koi_insol', 'koi_srho', 'koi_srad',
    'koi_smass', 'koi_steff', 'koi_slogg', 'koi_smet', 'koi_model_snr'
]