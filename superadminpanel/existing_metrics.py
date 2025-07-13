import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances

try:
    data_5m = pd.read_csv('superadminpanel/full_dataset_5m.csv')
except:
    try:
        data_5m = pd.read_csv('superadminpanel/full_dataset.csv')
    except:
        data_5m = pd.read_csv('superadminpanel/full_dataset_old.csv')

def demographic_parity(protected_df, nonprotected_df, threshold=0.1):
    p1 = protected_df["pred"].mean()
    p2 = nonprotected_df["pred"].mean()
    diff = abs(p1 - p2) * 100

    return {"value": round(diff, 2), "threshold": threshold, "fair": diff <= threshold}

def equal_opportunity(protected_df, nonprotected_df, threshold=0.1):
    p1 = protected_df[protected_df["label"] == 1]["pred"].mean()
    p2 = nonprotected_df[nonprotected_df["label"] == 1]["pred"].mean()
    diff = abs(p1 - p2) * 100
    return {"value": round(diff, 2), "threshold": threshold, "fair": diff <= threshold}

def predictive_equality(protected_df, nonprotected_df, threshold=0.1):
    p1 = protected_df[protected_df["label"] == 0]["pred"].mean()
    p2 = nonprotected_df[nonprotected_df["label"] == 0]["pred"].mean()
    diff = abs(p1 - p2) * 100
    return {"value": round(diff, 2), "threshold": threshold, "fair": diff <= threshold}

def outcome_test(protected_df, nonprotected_df, threshold=0.1):
    p1 = protected_df[protected_df["pred"] == 1]["label"].mean()
    p2 = nonprotected_df[nonprotected_df["pred"] == 1]["label"].mean()
    diff = abs(p1 - p2) * 100
    return {"value": round(diff, 2), "threshold": threshold, "fair": diff <= threshold}

def equalized_odds(protected_df, nonprotected_df, threshold=0.1):
    tpr1 = protected_df[protected_df["label"] == 1]["pred"].mean()
    tpr2 = nonprotected_df[nonprotected_df["label"] == 1]["pred"].mean()

    fpr1 = protected_df[protected_df["label"] == 0]["pred"].mean()
    fpr2 = nonprotected_df[nonprotected_df["label"] == 0]["pred"].mean()

    diff = (abs(tpr1 - tpr2) + abs(fpr1 - fpr2)) / 2 * 100
    return {"value": round(diff, 2), "threshold": threshold, "fair": diff <= threshold}

def conditional_statistical_parity(protected_df, nonprotected_df, threshold=0.1, group_cols=[]):
    diffs = []
    combined = pd.concat([
        protected_df.assign(group="protected"),
        nonprotected_df.assign(group="nonprotected")
    ])

    for _, subset in combined.groupby(group_cols):
        p_grp = subset[subset["group"] == "protected"]
        np_grp = subset[subset["group"] == "nonprotected"]
        if not p_grp.empty and not np_grp.empty:
            diff = abs(p_grp["pred"].mean() - np_grp["pred"].mean())
            diffs.append(diff)

    avg_diff = np.mean(diffs) if diffs else 0.0
    return {
        "value": round(avg_diff * 100, 2),
        "threshold": threshold,
        "fair": avg_diff <= threshold
    }

def consistency_score(df, features, k=5, threshold=0.1):
    X = df[features].values
    y = df["pred"].values
    distances = euclidean_distances(X, X)

    np.fill_diagonal(distances, np.inf)
    neighbor_indices = distances.argsort(axis=1)[:, :k]

    diffs = []
    for i in range(len(df)):
        neighbors = y[neighbor_indices[i]]
        diff = abs(y[i] - neighbors.mean())
        diffs.append(diff)

    consistency = 1 - np.mean(diffs)
    value = round(100 * (1 - consistency), 2)
    return {"value": value, "threshold": threshold, "fair": value <= threshold}

def counterfactual_fairness(df, col_a, col_b, threshold=0.1, fallback_data=data_5m):
    using_org = True

    def extract_base_col_and_value(col_str):
        base = col_str.split("[")[0].strip()
        value = col_str.split("[")[1].replace("]", "").strip()
        return base, value

    try:
        if col_a in df.columns and col_b in df.columns:
            print(f"[Info] Flipping between two separate columns: {col_a}, {col_b}")

            full_df = df.copy()
            flip_df = full_df.copy()
            flip_df[[col_a, col_b]] = flip_df[[col_b, col_a]]

            merge_cols = [col for col in df.columns if col not in ['pred', 'label']]
            matching_records = pd.merge(
                full_df[full_df[col_a] == True],
                flip_df[flip_df[col_a] == True],
                how='inner',
                on=merge_cols
            )

            if matching_records.empty:
                using_org = False
                full_df = fallback_data.copy()
                flip_df = full_df.copy()
                flip_df[[col_a, col_b]] = flip_df[[col_b, col_a]]
                matching_records = pd.merge(
                    full_df[full_df[col_a] == True],
                    flip_df[flip_df[col_a] == True],
                    how='inner',
                    on=merge_cols
                )

            if matching_records.empty:
                return {
                    "value": 0.0, "threshold": threshold, "fair": True,
                    "note": "No matching counterfactual pairs"
                }

            changed = (matching_records["pred_x"] != matching_records["pred_y"]).mean() * 100

        else:
            base_a, val_a = extract_base_col_and_value(col_a)
            base_b, val_b = extract_base_col_and_value(col_b)

            if base_a != base_b:
                return {
                    "value": 0.0, "threshold": threshold, "fair": True,
                    "note": f"Invalid base columns for value-based comparison: {base_a}, {base_b}"
                }

            print(f"[Info] Flipping values inside column '{base_a}': {val_a} ↔ {val_b}")
            base_col = base_a

            def parse_range(val):
                parts = val.replace(" to ", "-").split("-")
                return float(parts[0]), float(parts[1])

            min_a, max_a = parse_range(val_a)
            min_b, max_b = parse_range(val_b)

            group_a = df[(df[base_col] >= min_a) & (df[base_col] <= max_a)].copy()
            group_b = df[(df[base_col] >= min_b) & (df[base_col] <= max_b)].copy()

            if group_a.empty or group_b.empty:
                if fallback_data is None:
                    return {"value": 0.0, "threshold": threshold, "fair": True, "note": "No matching records"}
                using_org = False
                return counterfactual_fairness(fallback_data, col_a, col_b, threshold)

            group_a_cf = group_a.copy()
            group_b_cf = group_b.copy()

            group_a_cf[base_col] = group_b[base_col].median()
            group_b_cf[base_col] = group_a[base_col].median()

            merge_cols = [c for c in df.columns if c not in ['pred', 'label', base_col]]
            merged_a = group_a.merge(group_a_cf, on=merge_cols, suffixes=('_orig', '_cf'))
            merged_b = group_b.merge(group_b_cf, on=merge_cols, suffixes=('_orig', '_cf'))

            merged = pd.concat([merged_a, merged_b])

            if merged.empty:
                return {"value": 0.0, "threshold": threshold, "fair": True, "note": "No matching merged records"}

            changed = (merged["pred_orig"] != merged["pred_cf"]).mean() * 100

    except Exception as e:
        return {"value": 0.0, "threshold": threshold, "fair": True, "note": f"Error: {str(e)}"}

    print(f"[Result] Counterfactual Fairness - Changed: {changed:.2f}%, Threshold: {threshold}%")
    return {
        "value": round(changed, 2),
        "threshold": threshold,
        "fair": changed <= threshold,
        "note": "Synthesized data used" if not using_org else "Real data used"
    }
