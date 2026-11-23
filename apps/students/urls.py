from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('teachers/', views.student_teachers_view, name='student_teachers'),
    path('analytics/', views.student_analytics_view, name='student_analytics'),
]
