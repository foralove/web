from django.apps import AppConfig


class MarkdownRendererConfig(AppConfig):
    name = 'markdown_renderer'
    verbose_name = 'Markdown渲染器'
    
    def ready(self):
        pass 