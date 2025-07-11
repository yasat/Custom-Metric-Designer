import pandas as pd
import numpy as np
from core.features_data import FEATURE_CATEGORY_MAP
from .existing_metrics import *

data = pd.read_csv('superadminpanel/full_dataset.csv')


def parse_feature_tags(feature_str, df=data, feature_category_map=FEATURE_CATEGORY_MAP, return_columns=False):

    protected_mask = pd.Series([True] * len(df))
    non_protected_mask = pd.Series([True] * len(df))

    protected_cols = []
    non_protected_cols = []

    for item in feature_str.split(","):
        item = item.strip()
        if not item:
            continue

        try:
            parts = item.split("[")
            label = parts[0].strip()
            value = parts[1].split("]")[0].strip()
            tag = parts[2].split("]")[0].strip()
        except IndexError:
            raise ValueError(f"Invalid format: '{item}' — expected format 'Feature[Value][Tag]'")

        if label in feature_category_map:
            group_code = feature_category_map[label].get(value)
            if not group_code:
                raise ValueError(f"Unknown group '{value}' for categorical feature '{label}'")

            column = f"{label}[{group_code}]"
            if column not in df.columns:
                raise ValueError(f"Column '{column}' not found in dataset")

            condition = df[column] == True

        elif (
            any(s in value for s in ["-", " to "]) and 
            label in df.columns and 
            pd.api.types.is_numeric_dtype(df[label])
        ):
            parts_range = value.replace(" to ", "-").split("-")
            if len(parts_range) != 2:
                raise ValueError(f"Invalid numerical range: '{value}'")

            try:
                min_val = float(parts_range[0].strip())
                max_val = float(parts_range[1].strip())
            except ValueError:
                raise ValueError(f"Invalid numeric values in range '{value}' for '{label}'")

            condition = (df[label] >= min_val) & (df[label] <= max_val)

        else:
            raise ValueError(f"Unsupported or unrecognized feature: {label}[{value}]")

        if tag == "protected":
            protected_mask &= condition
            if 'column' in locals():
                protected_cols.append(column)
        elif tag == "non-protected":
            non_protected_mask &= condition
            if 'column' in locals():
                non_protected_cols.append(column)
        else:
            raise ValueError(f"Unknown tag '{tag}' in '{item}'")

    if return_columns:
        return df[protected_mask], df[non_protected_mask], protected_cols, non_protected_cols
    else:
        return df[protected_mask], df[non_protected_mask]
    

def parse_custom_condition_mask(conditions, df=data, feature_category_map=FEATURE_CATEGORY_MAP):

    mask = pd.Series([True] * len(df))

    for cond in conditions:
        label = cond.feature.strip()
        value = (cond.binning or "").strip().split("[")[-1].strip("]")

        print(f"[Processing Condition] {label}[{value}]")

        if not label or not value:
            print(f"[Skipping] Empty label or value in condition: {cond}")
            continue

        if label in feature_category_map:
            group_code = feature_category_map[label].get(value)
            if not group_code:
                print(f"[Missing Group Code] {label}[{value}] not found in FEATURE_CATEGORY_MAP")
                continue

            column = f"{label}[{group_code}]"
            if column not in df.columns:
                print(f"[Missing Column] {column} not in dataset")
                continue

            condition = df[column] == True

        elif (
            any(s in value for s in ["-", " to "]) and
            label in df.columns and
            pd.api.types.is_numeric_dtype(df[label])
        ):
            parts_range = value.replace(" to ", "-").split("-")
            if len(parts_range) != 2:
                print(f"[Invalid Range] {label}[{value}]")
                continue

            try:
                min_val = float(parts_range[0].strip())
                max_val = float(parts_range[1].strip())
                condition = (df[label] >= min_val) & (df[label] <= max_val)
            except Exception as e:
                print(f"[Range Error] {label}[{value}] → {e}")
                continue

        else:
            print(f"[Unsupported] {label}[{value}] is neither categorical nor range-matching")
            continue

        mask &= condition

    return mask

def compute_conditional_probability(df, conditions, probability_type):
    mask = parse_custom_condition_mask(conditions, df)
    sub_df = df[mask]

    if sub_df.empty:
        return 0.0

    if probability_type == "predicted_true":
        return (sub_df["pred"] == 1).mean()

    elif probability_type == "predicted_false":
        return (sub_df["pred"] == 0).mean()

    elif probability_type == "ground_truth_true":
        return (sub_df["label"] == 1).mean()

    elif probability_type == "ground_truth_false":
        return (sub_df["label"] == 0).mean()

    else:
        print(f"[Unsupported probability type] {probability_type}")
        return 0.0

def evaluate_combine_custom_own(cards, df, global_threshold):
    logic_chain = []
    card_outputs = []

    for i, card in enumerate(cards):
        conds = card.conditions.all()
        prob_type = card.probability_type
        op = card.boolean_operator or "AND"

        prob = compute_conditional_probability(df, conds, prob_type)

        print(f"[Card {i+1}] Conditions: {conds}, Probability Type: {prob_type}, Computed Probability: {prob}")
        result = prob >= global_threshold
        logic_chain.append((result, op))
        card_outputs.append({
            "probability": round(prob, 4),
            "threshold": global_threshold,
            "fair": result,
            "op": op,
            "card_id": card.id
        })

    # final_result = logic_chain[0][0]
    # for (val, op) in logic_chain[1:]:
    #     if op == "AND":
    #         final_result = final_result and val
    #     elif op == "OR":
    #         final_result = final_result or val

    custom_op_found = any(op not in ["AND", "OR"] for _, op in logic_chain)

    if custom_op_found:
        final_result = None
    else:
        final_result = logic_chain[0][0] if logic_chain else False
        prev_op = None
        for val, op in logic_chain:
            if prev_op is None:
                prev_op = op
                continue
            if prev_op == "AND":
                final_result = final_result and val
            elif prev_op == "OR":
                final_result = final_result or val
            prev_op = op

    return {
        "fair": final_result,
        "details": card_outputs
    }