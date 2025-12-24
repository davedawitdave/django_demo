import pandas as pd
import numpy as np
import os
import joblib
from pathlib import Path

CSV = Path(__file__).parent / 'house_price_clean.csv'
MODEL = Path(__file__).parent / 'ml_model.joblib'
SCALER = Path(__file__).parent / 'scaler.joblib'


def analyze(df):
    info = {}
    for col in df.columns:
        if col == 'price':
            continue
        s = df[col]
        if pd.api.types.is_integer_dtype(s) or pd.api.types.is_bool_dtype(s):
            vc = s.value_counts(normalize=True).to_dict()
            info[col] = {'type': 'categorical', 'probs': vc}
        else:
            info[col] = {'type': 'numeric', 'mean': float(s.mean()), 'std': float(s.std()), 'min': float(s.min()), 'max': float(s.max())}
    return info


def sample_value(col_info):
    if col_info['type'] == 'categorical':
        vals = list(col_info['probs'].keys())
        probs = list(col_info['probs'].values())
        return int(np.random.choice(vals, p=probs))
    else:
        # numeric: sample normal around mean, clip to min/max, ensure >=0
        val = np.random.normal(col_info['mean'], max(1e-6, col_info['std']))
        return float(max(0, np.clip(val, col_info['min'], col_info['max'])))


def generate_rows(df, n=20):
    info = analyze(df)
    cols = [c for c in df.columns if c != 'price']
    rows = []
    for _ in range(n):
        r = {}
        for c in cols:
            r[c] = sample_value(info[c])
        rows.append(r)
    new_df = pd.DataFrame(rows)
    # ensure integer columns that were int remain int
    for c in new_df.columns:
        if pd.api.types.is_integer_dtype(df[c]):
            new_df[c] = new_df[c].round().astype(int)
    return new_df


def compute_price_if_model(new_X):
    # If model and scaler exist, use them to compute price and add small noise
    if MODEL.exists() and SCALER.exists():
        model = joblib.load(MODEL)
        scaler = joblib.load(SCALER)
        # Ensure column order matches training data (use CSV's order)
        # The scaler was likely fit on df.drop('price').columns
        # We'll attempt to align by columns present in new_X
        X = new_X.copy()
        if hasattr(scaler, 'feature_names_in_'):
            cols = list(scaler.feature_names_in_)
            X = X[cols]
        X_scaled = scaler.transform(X)
        preds = model.predict(X_scaled)
        # add small gaussian noise (2% of mean)
        noise = np.random.normal(0, 0.02 * np.mean(preds), size=preds.shape)
        return np.round(preds + noise).astype(int)
    else:
        return None


if __name__ == '__main__':
    csv_path = os.path.join(os.path.dirname(__file__), 'house_price_clean.csv')

    # Load existing CSV
    df = pd.read_csv(csv_path)
    before = len(df)
    print('Rows before:', before)

    new_X = generate_rows(df, n=20)

    prices = compute_price_if_model(new_X)
    if prices is not None:
        new_X['price'] = prices
        print('Computed prices using model for generated rows.')
    else:
        # fallback: sample prices from existing distribution with noise
        sampled = df['price'].sample(len(new_X), replace=True).values
        noise = np.random.normal(0, 0.05 * np.mean(sampled), size=sampled.shape)
        new_X['price'] = np.round(sampled + noise).astype(int)
        print('Assigned prices by sampling existing distribution.')

    # reorder to original CSV column order
    cols = list(df.columns)
    new_X = new_X[cols]

    # append
    new_X.to_csv(csv_path, mode='a', header=False, index=False)

    after_append = len(pd.read_csv(csv_path))
    print(f'Appended 20 rows. Rows after append: {after_append}')

    # Clean negatives
    df_full = pd.read_csv(csv_path)
    negatives = df_full[(df_full < 0).any(axis=1)]
    if len(negatives) > 0:
        df_clean = df_full[(df_full >= 0).all(axis=1)]
        df_clean.to_csv(csv_path, index=False)
        print(f'Removed {len(negatives)} rows with negatives. Final rows: {len(df_clean)}')
    else:
        print('No negatives found.')
