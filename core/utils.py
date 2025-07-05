from .models import DesignCombineMetrics, DesignExistingMetrics, DesignCustomOwnMetric

def get_design_model(staging):
    if staging.metric_type == "combine_existing":
        return DesignCombineMetrics
    elif staging.metric_type == "custom_own":
        return DesignCustomOwnMetric
    else:
        return DesignExistingMetrics