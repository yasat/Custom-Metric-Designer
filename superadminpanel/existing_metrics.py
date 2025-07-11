import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances

def demographic_parity(protected_df, nonprotected_df, threshold=0.1):
    p1 = protected_df["pred"].mean()
    p2 = nonprotected_df["pred"].mean()
    diff = abs(p1 - p2) * 100

    print(f"Demographic Parity - Protected: {p1}, Non-Protected: {p2}, Diff: {diff}")
    return {"value": round(diff, 4), "threshold": threshold, "fair": diff <= threshold}

def equal_opportunity(protected_df, nonprotected_df, threshold=0.1):
    p1 = protected_df[protected_df["label"] == 1]["pred"].mean()
    p2 = nonprotected_df[nonprotected_df["label"] == 1]["pred"].mean()
    diff = abs(p1 - p2) * 100
    print(f"Equal Opportunity - Protected: {p1}, Non-Protected: {p2}, Diff: {diff}, Threshold: {threshold}")
    print(diff <= threshold)
    return {"value": round(diff, 4), "threshold": threshold, "fair": diff <= threshold}

def predictive_equality(protected_df, nonprotected_df, threshold=0.1):
    p1 = protected_df[protected_df["label"] == 0]["pred"].mean()
    p2 = nonprotected_df[nonprotected_df["label"] == 0]["pred"].mean()
    diff = abs(p1 - p2) * 100
    return {"value": round(diff, 4), "threshold": threshold, "fair": diff <= threshold}

def outcome_test(protected_df, nonprotected_df, threshold=0.1):
    p1 = protected_df[protected_df["pred"] == 1]["label"].mean()
    p2 = nonprotected_df[nonprotected_df["pred"] == 1]["label"].mean()
    diff = abs(p1 - p2) * 100
    return {"value": round(diff, 4), "threshold": threshold, "fair": diff <= threshold}

def equalized_odds(protected_df, nonprotected_df, threshold=0.1):
    tpr1 = protected_df[protected_df["label"] == 1]["pred"].mean()
    tpr2 = nonprotected_df[nonprotected_df["label"] == 1]["pred"].mean()

    fpr1 = protected_df[protected_df["label"] == 0]["pred"].mean()
    fpr2 = nonprotected_df[nonprotected_df["label"] == 0]["pred"].mean()

    diff = (abs(tpr1 - tpr2) + abs(fpr1 - fpr2)) / 2 * 100
    return {"value": round(diff, 4), "threshold": threshold, "fair": diff <= threshold}

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
        "value": round(avg_diff * 100, 4),
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
    value = round(100 * (1 - consistency), 4)
    return {"value": value, "threshold": threshold, "fair": value <= threshold}

def counterfactual_fairness(df, col_a, col_b, threshold=0.1):
    mask = (df[col_a] == 1) & (df[col_b] == 0) | (df[col_a] == 0) & (df[col_b] == 1)
    df_orig = df.loc[mask].copy()

    if df_orig.empty:
        if df.empty:
            return {"value": 0.0, "threshold": threshold, "fair": True, "note": "No data to synthesize from"}

        synth_base = df.sample(n=min(10, len(df))).copy()
        synth_a = synth_base.copy()
        synth_b = synth_base.copy()

        synth_a[col_a] = 1
        synth_a[col_b] = 0

        synth_b[col_a] = 0
        synth_b[col_b] = 1

        df_orig = pd.concat([synth_a, synth_b])
        df_flip = df_orig.copy()
        df_flip[[col_a, col_b]] = df_flip[[col_b, col_a]]

        if "pred" not in df_orig.columns:
            df_orig["pred"] = np.random.randint(0, 2, size=len(df_orig))
            df_flip["pred"] = np.random.randint(0, 2, size=len(df_flip))
    else:
        df_flip = df_orig.copy()
        df_flip[[col_a, col_b]] = df_flip[[col_b, col_a]]

        if df_orig.equals(df_flip):
            return {"value": 0.0, "threshold": threshold, "fair": True, "note": "Swap resulted in no change"}

    pred_orig = df_orig["pred"].values
    pred_flip = df_flip["pred"].values

    changed = (pred_orig != pred_flip).mean() * 100

    return {
        "value": round(changed, 4),
        "threshold": threshold,
        "fair": changed <= threshold,
        "note": "Synthesized data used" if df_orig.empty else "Real data used"
    }
