from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('fairness-category/', views.fairness_category, name='fairness_category'),
    path('fairness-category/<int:staging_id>/', views.fairness_category, name='fairness_category_with_id'),
    path('fairness-perspective/<int:staging_id>/', views.fairness_perspective, name='fairness_perspective'),
    path('metric-type/<int:staging_id>/', views.metric_type, name='metric_type'),
    path('summary/<int:staging_id>/', views.summary, name='summary'),

    path('start-designing/<int:staging_id>/', views.start_designing, name='start_designing'),

    path('design/existing/<int:staging_id>/', views.design_existing_intro, name='design_existing'),
    path('design/features/<int:staging_id>/', views.design_metric_features, name='design_metric_features'),
    path('design/metric/<int:staging_id>/', views.design_metric_select_metric, name='design_metric_select_metric'),
    path('design/threshold/<int:staging_id>/', views.design_metric_threshold, name='design_metric_threshold'),

    path('design/summary/<int:staging_id>/', views.design_metric_summary, name='design_metric_summary'),
    path('design/save_new/<int:staging_id>/', views.design_save_new, name='design_save_new'),
    path('design/existing/review_all/<int:staging_id>/', views.design_existing_review_all, name='design_existing_review_all'),
    path('design/delete/<int:staging_id>/', views.design_metric_delete, name='design_metric_delete'),
    
    path('design/combine_existing/<int:staging_id>/', views.design_combine_existing_intro, name='design_combine_existing'),
    path('design/combine_existing/review_all/<int:staging_id>/', views.design_combine_existing_review_all, name='design_combine_existing_review_all'),
    path('design/combine_existing/summary/final/<int:staging_id>/', views.design_combine_existing_final_summary, name='design_combine_existing_final_summary'),


    path('design/custom-own/<int:staging_id>/', views.design_custom_own, name='design_custom_own'),

    path('under_construction', views.under_construction, name='under_construction'),
]