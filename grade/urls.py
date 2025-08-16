"""
URL configuration for the GRADE app
"""
from django.urls import path, include
from . import views

app_name = 'grade'

urlpatterns = [
    # Web interface URLs
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    
    # API URLs
    path('api/projects/', views.api_project_list, name='api_project_list'),
    path('api/projects/<int:project_id>/', views.api_project_detail, name='api_project_detail'),
]
