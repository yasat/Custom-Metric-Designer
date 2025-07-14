from django.contrib import admin
from .models import *

@admin.register(Staging)
class StagingAdmin(admin.ModelAdmin):
    list_display = ['id', 'pid', 'category', 'perspective', 'metric_type', 'priority']
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
    list_display = ('id', 'sid', 'probability_type', 'boolean_operator', 'order', 'side', 'delete_flag')
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

@admin.register(DesignProceduralMetric)
class DesignProceduralMetricAdmin(admin.ModelAdmin):
    list_display = ('id', 'sid', 'label_type', 'boolean_operator', 'order', 'preview', 'delete_flag')
    list_filter = ['label_type']
    search_fields = ['label_type']

@admin.register(DesignProceduralCondition)
class DesignProceduralConditionAdmin(admin.ModelAdmin):
    list_display = ('id', 'metric', 'feature', 'value', 'logic_with_next')
    list_filter = ['feature', 'logic_with_next']
    search_fields = ['feature', 'value', 'logic_with_next']

@admin.register(DesignProceduralGlobal)
class DesignProceduralGlobalAdmin(admin.ModelAdmin):
    list_display = ('sid', 'metric_name', 'threshold')
    search_fields = ['metric_name']

@admin.register(AffordabilityDesign)
class AffordabilityDesignAdmin(admin.ModelAdmin):
    list_display = ('id', 'staging_id', 'metric_name', 'threshold', 'created_at', 'delete_flag')
    search_fields = ['metric_name', 'staging_id']


@admin.register(AffordabilityCard)
class AffordabilityCardAdmin(admin.ModelAdmin):
    list_display = ('id', 'design', 'side', 'feature', 'operator', 'value', 'created_at', 'delete_flag')
    list_filter = ['side', 'feature', 'operator']
    search_fields = ['feature', 'value']