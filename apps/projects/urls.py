from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.projects_list_view, name='projects_list'),
    path('create/', views.project_create_view, name='project_create'),
    path('<int:project_id>/', views.project_detail_view, name='project_detail'),
    path('<int:project_id>/status/', views.project_status_update_view, name='project_status_update'),
]
