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
    path('design/existing/features/<int:staging_id>/', views.design_existing_features, name='design_existing_features'),
    path('design/existing/metric/<int:staging_id>/', views.design_existing_select_metric, name='design_existing_select_metric'),
    path('design/existing/threshold/<int:staging_id>/', views.design_existing_threshold, name='design_existing_threshold'),
    path('design/existing/summary/<int:staging_id>/', views.design_existing_summary, name='design_existing_summary'),
    path('design/existing/save_new/<int:staging_id>/', views.design_existing_save_new, name='design_existing_save_new'),
    path('design/existing/review_all/<int:staging_id>/', views.design_existing_review_all, name='design_existing_review_all'),
    path('design/existing/delete/<int:staging_id>/', views.design_existing_delete, name='design_existing_delete'),
    
    path('design/combine-existing/<int:staging_id>/', views.design_combine_existing, name='design_combine_existing'),
    path('design/combine-existing/features/<int:staging_id>/<int:design_id>', views.combine_existing_features, name='design_combine_existing_features'),
    path('design/combine-existing/metric/<int:staging_id>/<int:design_id>', views.combine_existing_select_metric, name='design_combine_existing_select_metric'),
    path('design/combine/threshold/<int:staging_id>/<int:design_id>', views.combine_existing_threshold, name='combine_existing_threshold'),
    path('design/combine/summary/<int:staging_id>/<int:design_id>', views.combine_existing_summary, name='combine_existing_summary'),
    path('design/combine/save_new/<int:staging_id>/<int:design_id>', views.combine_existing_save_new, name='combine_existing_save_new'),
    path('design/combine/review_all/<int:staging_id>/<int:design_id>', views.combine_existing_review_all, name='combine_existing_review_all'),
    path('design/combine/delete/<int:staging_id>/<int:design_id>', views.combine_existing_delete, name='combine_existing_delete'),
    
    path('design/custom-own/<int:staging_id>/', views.design_custom_own, name='design_custom_own'),


    path('under_construction', views.under_construction, name='under_construction'),
]