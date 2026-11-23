from django.urls import path
from . import views

app_name = 'journal'

urlpatterns = [
    path('', views.journal_view, name='journal_view'),
    path('my-grades/', views.student_grades_view, name='student_grades'),
]
