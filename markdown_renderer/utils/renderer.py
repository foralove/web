"""
Markdown解析引擎

提供将Markdown转换为HTML的核心功能
"""
import os
import traceback
from typing import Union, Optional, Dict, Any, List
from pathlib import Path

import markdown
from django.conf import settings
from django.utils.safestring import mark_safe, SafeString
from django.core.exceptions import ValidationError

from .sanitizer import FileValidator


class MarkdownRenderer:
    """
    Markdown 解析渲染引擎
    
    提供Markdown转HTML的核心功能，包括语法扩展和安全处理
    """
    
    # 默认Markdown扩展
    DEFAULT_EXTENSIONS = [
        'tables',           # 表格支持
        'fenced_code',      # 代码块支持
        'codehilite',       # 代码高亮
        'toc',              # 目录生成
        'nl2br',            # 换行转换
        'sane_lists',       # 更智能的列表处理
        'smarty',           # 智能标点
        'meta',             # 元数据支持
        'mdx_math',         # 数学公式支持
    ]
    
    # 不安全的扩展，默认禁用
    UNSAFE_EXTENSIONS = [
        'raw_html',         # 原始HTML支持
    ]
    
    # Markdown扩展的默认配置
    DEFAULT_EXTENSION_CONFIGS = {
        'codehilite': {
            'css_class': 'highlight',
            'linenums': False,
            'guess_lang': True,
        },
        'toc': {
            'title': '目录',
            'permalink': False,
        },
        'mdx_math': {
            'enable_dollar_delimiter': True,  # 启用 $...$ 作为行内公式
            'add_preview': True,              # 添加预览
        }
    }
    
    @classmethod
    def get_markdown_extensions(cls) -> List[str]:
        """获取配置的Markdown扩展"""
        config = getattr(settings, 'MARKDOWN_RENDER', {})
        extensions = config.get('EXTENSIONS', cls.DEFAULT_EXTENSIONS)
        
        # 如果配置中明确启用了不安全扩展，则添加它们
        if config.get('ENABLE_UNSAFE_EXTENSIONS', False):
            extensions.extend(cls.UNSAFE_EXTENSIONS)
            
        return extensions
    
    @classmethod
    def get_extension_configs(cls) -> Dict[str, Dict[str, Any]]:
        """获取Markdown扩展的配置"""
        config = getattr(settings, 'MARKDOWN_RENDER', {})
        ext_configs = cls.DEFAULT_EXTENSION_CONFIGS.copy()
        
        # 合并用户配置
        user_configs = config.get('EXTENSION_CONFIGS', {})
        for ext_name, ext_config in user_configs.items():
            if ext_name in ext_configs:
                ext_configs[ext_name].update(ext_config)
            else:
                ext_configs[ext_name] = ext_config
                
        return ext_configs
    
    @classmethod
    def render_markdown_content(cls, content: str) -> SafeString:
        """
        渲染Markdown文本内容为HTML
        
        Args:
            content: Markdown格式的文本内容
            
        Returns:
            SafeString: 转换后的HTML内容
        """
        try:
            # 获取扩展和配置
            extensions = cls.get_markdown_extensions()
            extension_configs = cls.get_extension_configs()
            
            # 创建Markdown实例
            md = markdown.Markdown(
                extensions=extensions,
                extension_configs=extension_configs,
                output_format='html5'
            )
            
            # 转换Markdown为HTML
            html_content = md.convert(content)
            
            # 标记为安全字符串
            return mark_safe(html_content)
            
        except Exception as e:
            error_message = f"""
            <div class="markdown-error">
                <h3>Markdown渲染错误</h3>
                <p>{str(e)}</p>
            </div>
            """
            return mark_safe(error_message)
    
    @classmethod
    def render_markdown_file(cls, file_path: str) -> SafeString:
        """
        渲染Markdown文件为HTML
        
        Args:
            file_path: Markdown文件的路径
            
        Returns:
            SafeString: 转换后的HTML内容
        """
        try:
            # 验证文件
            validated_path = FileValidator.validate_file(file_path)
            
            # 尝试不同的编码读取文件内容
            content = None
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            
            for encoding in encodings:
                try:
                    with open(validated_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            # 如果所有编码都失败，使用二进制方式读取并尝试自动检测
            if content is None:
                with open(validated_path, 'rb') as f:
                    raw_content = f.read()
                    # 尝试检测编码
                    try:
                        import chardet
                        detected = chardet.detect(raw_content)
                        encoding = detected['encoding'] or 'utf-8'
                        content = raw_content.decode(encoding)
                    except (ImportError, UnicodeDecodeError):
                        # 如果chardet不可用或解码失败，使用latin-1作为最后手段
                        content = raw_content.decode('latin-1')
                
            # 渲染Markdown内容
            return cls.render_markdown_content(content)
            
        except ValidationError as e:
            # 处理验证错误
            error_message = f"""
            <div class="markdown-error markdown-validation-error">
                <h3>文件验证错误</h3>
                <p>{str(e)}</p>
            </div>
            """
            return mark_safe(error_message)
            
        except Exception as e:
            # 处理其他异常
            error_message = f"""
            <div class="markdown-error">
                <h3>Markdown渲染错误</h3>
                <p>文件: {file_path}</p>
                <p>错误: {str(e)}</p>
                <p>堆栈跟踪: {traceback.format_exc()}</p>
            </div>
            """
            return mark_safe(error_message)


def render_markdown(file_path: str) -> SafeString:
    """
    对外API：渲染Markdown文件为HTML
    
    Args:
        file_path: 文件系统绝对路径或文件对象
        
    Returns:
        SafeString: 安全的HTML字符串
        
    异常处理:
        统一捕获异常返回错误提示HTML
    """
    return MarkdownRenderer.render_markdown_file(file_path) 