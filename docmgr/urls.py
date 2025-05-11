"""docmgr URL配置"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import HomeView

urlpatterns = [
    # 管理界面
    path('admin/', admin.site.urls),
    
    # 认证和用户账户
    path('accounts/', include('accounts.urls')),
    
    # 文档管理
    path('documents/', include('documents.urls')),
    
    # 首页
    path('', HomeView.as_view(), name='home'),
]

# 开发环境添加媒体文件URL
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 