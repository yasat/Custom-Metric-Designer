from django.contrib import admin
from .models import Staging, DesignExistingMetrics, DesignCombineMetrics

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