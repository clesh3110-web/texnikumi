from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    path('', views.assignment_list_view, name='assignment_list'),
    path('create/', views.assignment_create_view, name='assignment_create'),
    path('<int:task_id>/', views.assignment_detail_view, name='assignment_detail'),
]
