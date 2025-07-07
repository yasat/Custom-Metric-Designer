from django.urls import path
from . import views

urlpatterns = [
    path('', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('<str:pid>/view/', views.superadmin_view_metrics, name='superadmin_view_metrics'),
]