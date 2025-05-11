"""
ASGI配置

它暴露了ASGI可调用对象作为模块级变量，名为``application``。

更多信息请参阅
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docmgr.settings')

application = get_asgi_application() 