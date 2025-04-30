from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_document, name='upload_document'),
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('simple/', views.SimpleDocumentListView.as_view(), name='simple_document_list'),
] 