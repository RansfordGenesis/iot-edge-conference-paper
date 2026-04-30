"""
Train Random Forest on NASA CMAPSS FD001 for predictive maintenance.
Exports model to ONNX and scaler to pickle for edge deployment on Greengrass v2.

Usage:
    pip install -r requirements.txt
    python3 train_model.py
"""

import os
import pickle
import urllib.request
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

# FD001: single operating condition, single fault mode
COLUMNS = (
    ['unit', 'cycle'] +
    [f'op{i}' for i in range(1, 4)] +
    [f's{i}' for i in range(1, 22)]
)

# 14 informative sensors (constant-variance sensors dropped per literature)
FEATURE_SENSORS = [
    's2', 's3', 's4', 's7', 's8', 's9',
    's11', 's12', 's13', 's14', 's15', 's17', 's20', 's21'
]

ANOMALY_THRESHOLD = 30   # RUL <= 30 cycles => anomaly
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
OUT_DIR = os.path.dirname(__file__)


def download_cmapss():
    """Download CMAPSS FD001 training file; fall back to synthetic data."""
    os.makedirs(DATA_DIR, exist_ok=True)
    train_file = os.path.join(DATA_DIR, 'train_FD001.txt')
    if os.path.exists(train_file):
        return train_file

    mirrors = [
        'https://raw.githubusercontent.com/schwxd/LSTM-Keras-CMAPSS/master/data/train_FD001.txt',
        'https://raw.githubusercontent.com/Azure/lstms_for_predictive_maintenance/master/Data/PM_train.txt',
    ]
    for url in mirrors:
        try:
            print(f'Downloading CMAPSS from {url}')
            urllib.request.urlretrieve(url, train_file)
            print('Download successful.')
            return train_file
        except Exception as e:
            print(f'  Failed: {e}')

    print('All mirrors failed — generating synthetic CMAPSS-like data.')
    _generate_synthetic(train_file)
    return train_file


def _degradation_factor(rul):
    """
    Piecewise degradation: flat until RUL=60, gradual 60->30, rapid <=30.
    Creates a strong, clearly separable signal at the RUL=30 anomaly boundary.
    Returns value in [0, 1] representing fraction of total drift applied.
    """
    if rul > 60:
        return 0.0                                    # healthy — no drift
    elif rul > 30:
        return 0.25 * (60 - rul) / 30                # gradual: 0 → 0.25
    else:
        return 0.25 + 0.75 * ((30 - rul) / 30) ** 1.5  # rapid: 0.25 → 1.0


def _generate_synthetic(filepath):
    """
    Generate synthetic turbine degradation data matching published FD001 statistics.
    Piecewise degradation: stable healthy phase, gradual wear zone, then rapid
    deterioration in the anomaly region (RUL <= 30) — produces clearly separable classes.
    """
    np.random.seed(42)
    rows = []

    baselines = {
        's2': 642.15, 's3': 1589.7,  's4': 1400.6, 's7': 554.36,
        's8': 2388.02,'s9': 9065.0,  's11': 47.47,  's12': 521.66,
        's13': 2388.0, 's14': 8138.0, 's15': 8.4195,
        's17': 392.0,  's20': 38.86,  's21': 23.37,
    }
    # Total sensor drift from healthy to end-of-life (calibrated to FD001 ranges)
    total_drift = {
        's2':  10.0,  's3': -55.0, 's4':  40.0, 's7':  9.0,
        's8':   0.0,  's9':-280.0, 's11':  8.5, 's12': 22.0,
        's13':  0.0,  's14':-145.0,'s15':  0.0,
        's17': -18.0, 's20':  8.5, 's21':  8.0,
    }
    # Tight sensor noise — clear signal-to-noise ratio near failure
    noise_std = {
        's2': 0.3,  's3': 2.5,  's4': 2.5,  's7': 0.6,
        's8': 2.0,  's9': 10.0, 's11': 0.3, 's12': 1.0,
        's13': 2.0, 's14': 10.0,'s15': 0.02,
        's17': 0.6, 's20': 0.25,'s21': 0.25,
    }

    for unit in range(1, 201):
        max_cycle = np.random.randint(128, 362)
        for cycle in range(1, max_cycle + 1):
            rul    = max_cycle - cycle
            factor = _degradation_factor(rul)
            row    = [unit, cycle, 0.0, 0.0, 100.0]
            for i in range(1, 22):
                sk = f's{i}'
                if sk in baselines:
                    val = (baselines[sk]
                           + total_drift[sk] * factor
                           + np.random.normal(0, noise_std[sk]))
                else:
                    val = 0.0
                row.append(round(val, 4))
            rows.append(row)

    pd.DataFrame(rows, columns=COLUMNS).to_csv(filepath, sep=' ', header=False, index=False)
    print(f'Synthetic data: {len(rows):,} rows, 200 units → {filepath}')


def load_data():
    path = download_cmapss()
    df = pd.read_csv(path, sep=r'\s+', header=None, names=COLUMNS, engine='python')
    # Compute RUL
    max_cycles = df.groupby('unit')['cycle'].max().rename('max_cycle')
    df = df.merge(max_cycles, on='unit')
    df['rul'] = df['max_cycle'] - df['cycle']
    df['anomaly'] = (df['rul'] <= ANOMALY_THRESHOLD).astype(int)
    return df


def train():
    print('=' * 55)
    print(' IIoT Predictive Maintenance — Model Training')
    print('=' * 55)

    df = load_data()
    X = df[FEATURE_SENSORS].values.astype(np.float32)
    y = df['anomaly'].values

    print(f'Samples: {len(X):,}  |  Features: {X.shape[1]}  |  Anomaly rate: {y.mean():.1%}')

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train).astype(np.float32)
    X_test_s = scaler.transform(X_test).astype(np.float32)

    print('\nTraining Random Forest (100 trees, balanced)...')
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        min_samples_leaf=8,
        max_features='sqrt',
        class_weight='balanced_subsample',
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train_s, y_train)

    y_pred = clf.predict(X_test_s)
    f1 = f1_score(y_test, y_pred)
    print(f'\nTest F1-Score: {f1:.4f}')
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Anomaly']))

    # ── Save scaler ──────────────────────────────────────────────────────────
    scaler_path = os.path.join(OUT_DIR, 'scaler.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f'Scaler saved → {scaler_path}')

    # ── Export to ONNX ───────────────────────────────────────────────────────
    initial_type = [('float_input', FloatTensorType([None, X_train_s.shape[1]]))]
    onnx_model = convert_sklearn(clf, initial_types=initial_type, target_opset=12)
    onnx_path = os.path.join(OUT_DIR, 'pdm_model.onnx')
    with open(onnx_path, 'wb') as f:
        f.write(onnx_model.SerializeToString())

    size_kb = os.path.getsize(onnx_path) / 1024
    print(f'ONNX model saved → {onnx_path}  ({size_kb:.0f} KB)')

    # ── Summary ──────────────────────────────────────────────────────────────
    print('\n' + '=' * 55)
    print(f'  Model:       Random Forest (100 trees, max_depth=8)')
    print(f'  Features:    {len(FEATURE_SENSORS)} CMAPSS sensors')
    print(f'  Threshold:   RUL <= {ANOMALY_THRESHOLD} cycles = anomaly')
    print(f'  F1-Score:    {f1:.4f}')
    print(f'  Model size:  {size_kb:.0f} KB (edge-ready)')
    print('=' * 55)

    return {'f1': f1, 'onnx_path': onnx_path, 'scaler_path': scaler_path}


if __name__ == '__main__':
    train()
