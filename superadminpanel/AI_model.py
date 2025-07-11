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