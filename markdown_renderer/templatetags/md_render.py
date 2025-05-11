"""
Markdown渲染模板标签

提供在Django模板中渲染Markdown的标签
"""
from typing import Optional, Union, Dict, Any
import os

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import SafeString

from markdown_renderer.utils import render_markdown

register = template.Library()


@register.simple_tag
def render_markdown(file_path: str = None, file_obj = None) -> SafeString:
    """
    渲染Markdown文件为HTML的模板标签
    
    可以接受文件路径或文件对象作为参数
    
    用法:
    {% load md_render %}
    {% render_markdown file_path="/path/to/file.md" %}
    或
    {% render_markdown file_obj=document.file %}
    
    Args:
        file_path: Markdown文件路径
        file_obj: 文件对象(例如Django的FileField)
        
    Returns:
        SafeString: 渲染后的HTML内容
    """
    error_html = """
    <div class="markdown-error">
        <h3>参数错误</h3>
        <p>必须提供file_path或file_obj参数</p>
    </div>
    """
    
    # 检查是否提供了文件路径或文件对象
    if file_path is None and file_obj is None:
        return SafeString(error_html)
    
    # 如果提供了文件对象，获取其路径
    if file_obj is not None:
        try:
            file_path = file_obj.path
        except (AttributeError, ValueError) as e:
            error_html = f"""
            <div class="markdown-error">
                <h3>文件对象错误</h3>
                <p>{str(e)}</p>
            </div>
            """
            return SafeString(error_html)
    
    # 渲染Markdown文件
    return render_markdown(file_path)


@register.filter(name='markdown')
@stringfilter
def markdown_filter(value: str) -> SafeString:
    """
    将Markdown文本内容转换为HTML的模板过滤器
    
    用法:
    {% load md_render %}
    {{ content|markdown }}
    
    Args:
        value: Markdown格式的文本内容
        
    Returns:
        SafeString: 渲染后的HTML内容
    """
    from markdown_renderer.utils.renderer import MarkdownRenderer
    return MarkdownRenderer.render_markdown_content(value) 