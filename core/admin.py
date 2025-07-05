from django.contrib import admin
from .models import (
    Staging,
    DesignExistingMetrics,
    DesignCombineMetrics,
    DesignCustomOwnMetric,
    DesignCustomOwnCondition,
    DesignCustomOwnGlobal
)

@admin.register(Staging)
class StagingAdmin(admin.ModelAdmin):
    list_display = ['id', 'pid', 'category', 'perspective', 'metric_type']
    search_fields = ['pid', 'category', 'perspective', 'metric_type']
    list_filter = ['category', 'perspective', 'metric_type']

@admin.register(DesignExistingMetrics)
class DesignExistingMetricsAdmin(admin.ModelAdmin):
    list_display = ('id', 'sid', 'features', 'metric', 'threshold', 'delete_flag')

@admin.register(DesignCombineMetrics)
class DesignCombineMetricsAdmin(admin.ModelAdmin):
    list_display = ('id', 'sid', 'features', 'metric', 'threshold', 'weight', 'group_level', 'boolean_operator', 'order', 'delete_flag')

@admin.register(DesignCustomOwnMetric)
class DesignCustomOwnMetricAdmin(admin.ModelAdmin):
    list_display = ('id', 'sid', 'probability_type', 'boolean_operator', 'order', 'delete_flag')
    list_filter = ['probability_type']
    search_fields = ['probability_type']

@admin.register(DesignCustomOwnCondition)
class DesignCustomOwnConditionAdmin(admin.ModelAdmin):
    list_display = ('id', 'metric', 'feature', 'binning', 'logic_with_next')
    list_filter = ['feature', 'logic_with_next']
    search_fields = ['feature', 'binning', 'logic_with_next']

@admin.register(DesignCustomOwnGlobal)
class DesignCustomOwnGlobalAdmin(admin.ModelAdmin):
    list_display = ('sid', 'metric_name', 'threshold')
    search_fields = ['metric_name']
