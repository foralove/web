"""docmgr URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import HomeView

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Authentication and user accounts
    path('accounts/', include('accounts.urls')),
    
    # Document management
    path('documents/', include('documents.urls')),
    
    # Home page
    path('', HomeView.as_view(), name='home'),
]

# Add URL patterns for serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 