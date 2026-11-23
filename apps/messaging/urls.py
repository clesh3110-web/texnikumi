from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox_view, name='inbox'),
    path('sent/', views.sent_view, name='sent'),
    path('compose/', views.compose_view, name='compose'),
    path('<int:message_id>/', views.message_detail_view, name='message_detail'),
    path('<int:message_id>/delete/', views.delete_message_view, name='delete_message'),
]
