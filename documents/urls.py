from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('upload/', views.upload_document, name='upload_document'),
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('simple/', views.SimpleDocumentListView.as_view(), name='simple_document_list'),
    path('<int:doc_id>/', views.document_view, name='document_view'),
    
    # 重定向错误的URL格式
    path('view/<int:doc_id>/', RedirectView.as_view(pattern_name='document_view'), name='document_view_redirect'),
] 