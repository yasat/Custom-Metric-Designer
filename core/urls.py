from django.urls import path, include
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

    path('design/custom-own/<int:staging_id>/', views.custom_own_intro, name='custom_own_intro'),
    path('design/custom-own/<int:staging_id>/select-mode/', views.custom_own_select_mode, name='custom_own_select_mode'),
    path('design/custom-own/<int:staging_id>/card/<int:card_id>/', views.custom_own_card_edit, name='custom_own_card_edit'),
    path('design/custom-own/<int:staging_id>/card/new/', views.custom_own_card_new, name='custom_own_card_new'),
    path('design/custom-own/<int:staging_id>/logic-review/', views.custom_own_logic_review, name='custom_own_logic_review'),
    path("design/custom/own/<int:staging_id>/logic-review/<str:side>/", views.custom_own_logic_review, name="custom_own_logic_review_side"),
    path('design/custom-own/<int:staging_id>/set-threshold/', views.custom_own_set_threshold, name='custom_own_set_threshold'),
    path('design/custom-own/<int:staging_id>/final-review/', views.custom_own_final_review, name='custom_own_final_review'),

    path('design/custom-own/<int:staging_id>/compare/', views.custom_own_compare, name='custom_own_compare'),
    path('design/custom-own/<int:staging_id>/compare/card/<str:side>/new/', views.custom_own_card_new_compare, name='custom_own_card_new_compare'),
    path('design/custom-own/<int:staging_id>/compare/card/<int:card_id>/edit/', views.custom_own_card_edit_compare, name='custom_own_card_edit_compare'),
    path('design/custom-own/<int:staging_id>/compare/card/<int:card_id>/delete/', views.custom_own_card_delete, name='custom_own_card_delete'),
    path('design/custom-own/<int:staging_id>/compare/set-threshold/', views.custom_own_compare_set_threshold, name='custom_own_compare_set_threshold'),
    path('design/custom-own/<int:staging_id>/compare/final-review/', views.custom_own_compare_final_review, name='custom_own_compare_final_review'),

    path('procedural/intro/<int:staging_id>/', views.procedural_intro, name='procedural_intro'),
    path('procedural/builder/<int:staging_id>/', views.procedural_builder, name='procedural_builder'),
    path('procedural/set-threshold/<int:staging_id>/', views.procedural_set_threshold, name='procedural_set_threshold'),
    path('procedural/final-review/<int:staging_id>/', views.procedural_final_review, name='procedural_final_review'),
    path('procedural/<int:staging_id>/add-card/', views.save_procedural_card, name='save_procedural_card'),

    path('affordability/intro/<int:staging_id>/', views.affordability_intro, name='affordability_intro'),
    path('affordability/builder/<int:staging_id>/', views.affordability_builder, name='affordability_builder'),
    path('affordability/set-threshold/<int:staging_id>/', views.affordability_set_threshold, name='affordability_set_threshold'),
    path('affordability/final-review/<int:staging_id>/', views.affordability_final_review, name='affordability_final_review'),
    path('affordability/<int:staging_id>/add-card/', views.save_affordability_card, name='save_affordability_card'),
    path('affordability/<int:staging_id>/delete-card/', views.delete_affordability_card, name='delete_affordability_card'),

    path('under_construction', views.under_construction, name='under_construction'),

    path('superadmin/', include('superadminpanel.urls')),
]