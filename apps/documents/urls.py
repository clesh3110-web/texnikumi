from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.documents_list_view, name='documents_list'),
    path('my-documents/', views.student_upload_document_view, name='student_documents'),
    path('<int:doc_id>/', views.document_detail_view, name='document_detail'),
]
