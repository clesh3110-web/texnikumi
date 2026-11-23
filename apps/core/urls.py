from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Ommaviy veb-sayt yo'nalishlari
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('leadership/', views.leadership_view, name='leadership'),
    path('departments/', views.departments_view, name='departments'),
    path('news/', views.news_list_view, name='news_list'),
    path('news/<int:pk>/', views.news_detail_view, name='news_detail'),
    path('contact/', views.contact_view, name='contact'),

    # Administrator boshqaruv paneli yo'nalishlari
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-dashboard/groups/<int:group_id>/', views.admin_group_detail_view, name='admin_group_detail'),
    path('admin-dashboard/students/', views.admin_students_list_view, name='admin_students'),
    path('admin-dashboard/teachers/', views.admin_teachers_list_view, name='admin_teachers'),
]
