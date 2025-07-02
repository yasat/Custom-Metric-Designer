from django.contrib import admin
from .models import Staging, DesignExistingMetrics, DesignCombineExistingMetricsMain, DesignCombineExistingMetricsSub

@admin.register(Staging)
class StagingAdmin(admin.ModelAdmin):
    list_display = ['id', 'pid', 'category', 'perspective', 'metric_type']
    search_fields = ['pid', 'category', 'perspective', 'metric_type']
    list_filter = ['category', 'perspective', 'metric_type']

@admin.register(DesignExistingMetrics)
class DesignExistingMetricsAdmin(admin.ModelAdmin):
    list_display = ('id', 'sid', 'features', 'metric', 'threshold', 'delete_flag')

@admin.register(DesignCombineExistingMetricsMain)
class DesignCombineExistingMetricsMainAdmin(admin.ModelAdmin):
    list_display = ('id', 'sid', 'delete_flag')

@admin.register(DesignCombineExistingMetricsSub)
class DesignCombineExistingMetricsSubAdmin(admin.ModelAdmin):
    list_display = ('id', 'group_id', 'priority_id', 'features', 'metric', 'threshold', 'weightage', 'next_condition', 'delete_flag')