from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.timetable_view, name='timetable_view'),
    path('item/<int:item_id>/book/', views.timetable_book_action_view, name='timetable_book_action'),
    path('request-book/<int:subject_id>/', views.request_book_view, name='request_book'),
]
