from .models import DesignCombineMetrics, DesignExistingMetrics, DesignCustomOwnMetric

from .features_data import FEATURES

def get_design_model(staging):
    if staging.metric_type == "combine_existing":
        return DesignCombineMetrics
    elif staging.metric_type == "custom_own":
        return DesignCustomOwnMetric
    else:
        return DesignExistingMetrics

def get_operator_options():
    return ['=', '≠', '<', '<=', '>', '>=']

def get_group_options():
    """
    Generate group options from categorical features.
    Output format: "Feature Name (Category)"
    """
    group_options = []
    for feature in FEATURES:
        if feature['type'] == 'categorical':
            for category in feature['categories']:
                group_options.append(f"{feature['name']} ({category})")
    return group_options