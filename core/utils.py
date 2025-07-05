from .models import DesignCombineMetrics, DesignExistingMetrics

def get_design_model(staging):
    if staging.metric_type == "combine_existing":
        return DesignCombineMetrics
    else:
        return DesignExistingMetrics