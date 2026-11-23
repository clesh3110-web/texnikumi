from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.library_catalog_view, name='catalog'),
    path('<int:book_id>/', views.book_detail_view, name='book_detail'),
]
