from django.urls import path
from . import views

urlpatterns = [
    path('', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('<str:pid>/view/', views.superadmin_view_metrics, name='superadmin_view_metrics'),
    path('admin/reorder/<str:pid>/', views.reorder_staging_view, name='reorder_staging_view'),
    path('admin/export/', views.export_metrics_excel, name='export_metrics_excel'),
]