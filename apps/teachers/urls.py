from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('dashboard/', views.teacher_dashboard_view, name='teacher_dashboard'),
    path('groups/', views.teacher_groups_view, name='teacher_groups'),
    path('groups/<int:group_id>/', views.teacher_group_detail_view, name='teacher_group_detail'),
    path('students/<int:student_id>/', views.teacher_student_detail_view, name='teacher_student_detail'),
]
