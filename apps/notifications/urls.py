from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_list_view, name='notifications_list'),
    path('<int:notif_id>/read/', views.mark_as_read_view, name='mark_read'),
    path('mark-all-read/', views.mark_all_read_view, name='mark_all_read'),
    path('api/unread-count/', views.unread_count_api, name='unread_count_api'),
]
