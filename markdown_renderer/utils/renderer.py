import os
import traceback
import base64
import re
from typing import Union, Optional, Dict, Any, List
from pathlib import Path

import markdown
from django.conf import settings
from django.utils.safestring import mark_safe, SafeString
from django.core.exceptions import ValidationError

from .sanitizer import FileValidator


class MarkdownRenderer:
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
    
    UNSAFE_EXTENSIONS = [
        'raw_html',
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
            'enable_dollar_delimiter': True, 
            'add_preview': True, 
        },
        'tables': {
            'use_align_attribute': True
        }
    }
    
    @classmethod
    def get_markdown_extensions(cls) -> List[str]:
        config = getattr(settings, 'MARKDOWN_RENDER', {})
        extensions = config.get('EXTENSIONS', cls.DEFAULT_EXTENSIONS)
        
        # 确保tables扩展被包含
        if 'tables' not in extensions:
            extensions.append('tables')
            
        if config.get('ENABLE_UNSAFE_EXTENSIONS', False):
            extensions.extend(cls.UNSAFE_EXTENSIONS)
            
        return extensions
    
    @classmethod
    def get_extension_configs(cls) -> Dict[str, Dict[str, Any]]:
        config = getattr(settings, 'MARKDOWN_RENDER', {})
        ext_configs = cls.DEFAULT_EXTENSION_CONFIGS.copy()
        
        user_configs = config.get('EXTENSION_CONFIGS', {})
        for ext_name, ext_config in user_configs.items():
            if ext_name in ext_configs:
                ext_configs[ext_name].update(ext_config)
            else:
                ext_configs[ext_name] = ext_config
                
        return ext_configs
    
    @classmethod
    def _process_image_links(cls, content: str, file_path: str) -> str:
        def replace_image(match):
            alt_text = match.group(1)
            img_path = match.group(2).strip()
            
            if img_path.startswith(('http://', 'https://', 'data:')):
                return f"![{alt_text}]({img_path})"
                
            if not os.path.isabs(img_path):
                base_dir = os.path.dirname(os.path.abspath(file_path))
                
                if img_path.startswith('./images/') or img_path.startswith('images/'):
                    full_path = os.path.normpath(os.path.join(base_dir, img_path))

                    if not os.path.exists(full_path):
                        markdown_root = r'E:\GitHub\markdown'
                        if img_path.startswith('./'):
                            img_path = img_path[2:]  # 移除开头的 ./
                        full_path = os.path.normpath(os.path.join(markdown_root, img_path))
                        
                    img_path = full_path
                else:
                    img_path = os.path.normpath(os.path.join(base_dir, img_path))
        
            print(f"处理图片: alt='{alt_text}', 路径='{img_path}'")
            
            if not os.path.exists(img_path):
                error_msg = f"""
                <div style="color: red; border: 1px solid red; padding: 10px; margin: 10px 0; background-color: #ffeeee;">
                    <strong>图片加载错误:</strong> 文件不存在 - {img_path}
                </div>
                """
                print(f"图片未找到: {img_path}")
                return error_msg
            
            try:
                with open(img_path, 'rb') as img_file:
                    img_data = img_file.read()
                    
                import mimetypes
                mime_type, _ = mimetypes.guess_type(img_path)
                if not mime_type:
                    ext = os.path.splitext(img_path.lower())[1]
                    mime_map = {
                        '.png': 'image/png',
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.gif': 'image/gif',
                        '.bmp': 'image/bmp',
                        '.webp': 'image/webp',
                        '.svg': 'image/svg+xml'
                    }
                    mime_type = mime_map.get(ext, 'image/png')
                
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                data_uri = f"data:{mime_type};base64,{img_base64}"
                
                print(f"图片加载成功: {img_path}，大小: {len(img_data)} 字节")
                return f"![{alt_text}]({data_uri})"
            except Exception as e:
                error_msg = f"""
                <div style="color: red; border: 1px solid red; padding: 10px; margin: 10px 0; background-color: #ffeeee;">
                    <strong>图片加载错误:</strong> {str(e)} <br>
                    <strong>图片路径:</strong> {img_path}
                </div>
                """
                print(f"图片加载错误 {img_path}: {str(e)}")
                return error_msg
        
        print(f"处理Markdown文件中的图片: {file_path}")
        
        img_pattern = r'!\[(.*?)\]\s*\((.*?)\)'
        processed = re.sub(img_pattern, replace_image, content)
        
        if '![' in content:
            print(f"原始内容中的图片引用数量: {content.count('![')}")
            print(f"处理后内容中的图片引用数量: {processed.count('![')}")
            
        return processed
    
    @classmethod
    def _add_table_styles(cls, html_content: str) -> str:
        """为所有表格添加Bootstrap样式"""
        # 将普通表格转换为Bootstrap样式表格
        html_content = html_content.replace('<table>', '<table class="table table-bordered table-striped">')
        
        # 查找表格
        table_pattern = r'<table[^>]*>'
        tables = re.findall(table_pattern, html_content)
        
        # 检查是否需要添加样式
        for table in tables:
            if 'class=' not in table:
                styled_table = table.replace('<table', '<table class="table table-bordered table-striped"')
                html_content = html_content.replace(table, styled_table)
            elif 'table ' not in table and 'table"' not in table:
                styled_table = table.replace('class="', 'class="table table-bordered table-striped ')
                html_content = html_content.replace(table, styled_table)
        
        # 添加表格容器样式，使表格可滚动
        html_content = re.sub(
            r'(<table[^>]*>.*?</table>)',
            r'<div class="table-responsive">\1</div>',
            html_content,
            flags=re.DOTALL
        )
        
        return html_content
    
    @classmethod
    def render_markdown_content(cls, content: str, file_path: Optional[str] = None) -> SafeString:
        try:
            # 处理图片链接
            if file_path:
                content = cls._process_image_links(content, file_path)
                
            extensions = cls.get_markdown_extensions()
            extension_configs = cls.get_extension_configs()
            
            md = markdown.Markdown(
                extensions=extensions,
                extension_configs=extension_configs,
                output_format='html5'
            )
            
            html_content = md.convert(content)
            
            # 处理表格样式
            html_content = cls._add_table_styles(html_content)
            
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
        try:
            validated_path = FileValidator.validate_file(file_path)
            
            content = None
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            
            for encoding in encodings:
                try:
                    with open(validated_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    
                    # 检查是否有乱码（Unicode替换字符）
                    if '\ufffd' not in content[:100]:
                        break
                except UnicodeDecodeError:
                    continue
            
            if content is None or '\ufffd' in content[:100]:
                with open(validated_path, 'rb') as f:
                    raw_content = f.read()
                    try:
                        import chardet
                        detected = chardet.detect(raw_content)
                        encoding = detected['encoding'] or 'utf-8'
                        content = raw_content.decode(encoding)
                    except (ImportError, UnicodeDecodeError):
                        content = raw_content.decode('latin-1')
                
            return cls.render_markdown_content(content, validated_path)
            
        except ValidationError as e:
            error_message = f"""
            <div class="markdown-error markdown-validation-error">
                <h3>文件验证错误</h3>
                <p>{str(e)}</p>
            </div>
            """
            return mark_safe(error_message)
            
        except Exception as e:
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
    return MarkdownRenderer.render_markdown_file(file_path) 