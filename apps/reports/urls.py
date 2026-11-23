from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard_view, name='dashboard'),
    path('export/attendance/', views.export_attendance_excel, name='export_attendance_excel'),
    path('export/grades/', views.export_grades_excel, name='export_grades_excel'),
    path('export/transcript/<int:student_id>/', views.export_student_transcript_pdf, name='export_student_transcript_pdf'),
]
