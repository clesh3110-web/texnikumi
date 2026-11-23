from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_view, name='attendance_view'),
    path('my-attendance/', views.student_attendance_view, name='student_attendance'),
    path('api/group-students-status/', views.group_students_status_api, name='api_group_students_status'),
]
