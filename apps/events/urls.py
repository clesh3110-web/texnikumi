from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.events_list_view, name='event_list'),
    path('<int:event_id>/', views.event_detail_view, name='event_detail'),
    path('<int:event_id>/register/', views.event_register_view, name='event_register'),
]
