import os
import mimetypes
from pathlib import Path
from typing import Union, Optional, Tuple, List
from django.conf import settings
from django.core.exceptions import ValidationError


class FileValidator:
    
    ALLOWED_EXTENSIONS = (
        # 文本文件
        '.md', '.markdown', '.txt', '.log', '.ini', '.conf', '.cfg', '.properties',
        # 代码文件
        '.html', '.htm', '.xml', '.json', '.yaml', '.yml', '.css', '.js', '.py', '.java', '.c', '.cpp', '.cs', '.php',
        # 图片文件
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp',
        # PDF文档
        '.pdf',
        # Office文档
        '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    )
    
    ALLOWED_MIMETYPES = (
        # 文本文件
        'text/markdown', 'text/plain', 'text/html', 'text/xml', 'application/json', 
        'application/xml', 'text/css', 'application/javascript',
        # 图片文件
        'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/svg+xml', 'image/webp',
        # PDF文档
        'application/pdf',
        # Office文档
        'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    )
    
    DEFAULT_MAX_SIZE = 10 * 1024 * 1024  # 增加到10MB
    
    @classmethod
    def get_max_size(cls) -> int:
        config = getattr(settings, 'MARKDOWN_RENDER', {})
        return config.get('MAX_SIZE', cls.DEFAULT_MAX_SIZE)

    @classmethod
    def validate_extension(cls, file_path: str) -> bool:
        _, ext = os.path.splitext(file_path.lower())
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValidationError(f"不支持的文件类型: {ext}。请上传支持的文件类型。")
        return True
    
    @classmethod
    def validate_mimetype(cls, file_path: str) -> bool:
        mime_type, _ = mimetypes.guess_type(file_path)
        
        if not mime_type and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                header = f.read(512)
                try:
                    header.decode('utf-8')
                    mime_type = 'text/plain'
                except UnicodeDecodeError:
                    mime_type = 'application/octet-stream'
        
        if mime_type not in cls.ALLOWED_MIMETYPES:
            raise ValidationError(f"不支持的MIME类型: {mime_type}。仅支持 {', '.join(cls.ALLOWED_MIMETYPES)}")
        return True
    
    @classmethod
    def validate_size(cls, file_path: str) -> bool:
        if not os.path.exists(file_path):
            raise ValidationError(f"文件不存在: {file_path}")
            
        file_size = os.path.getsize(file_path)
        max_size = cls.get_max_size()
        
        if file_size > max_size:
            raise ValidationError(f"文件大小({file_size}字节)超过允许的最大值({max_size}字节)")
        return True
    
    @classmethod
    def sanitize_path(cls, file_path: str) -> str:
        abs_path = os.path.abspath(file_path)
        print(f"验证文件路径: {file_path}")
        print(f"绝对路径: {abs_path}")
        
        allowed_paths = []
        
        if hasattr(settings, 'MEDIA_ROOT'):
            allowed_paths.append(os.path.abspath(settings.MEDIA_ROOT))
            
        if hasattr(settings, 'BASE_DIR'):
            allowed_paths.append(os.path.abspath(settings.BASE_DIR))
        
        # 添加外部目录支持
        config = getattr(settings, 'MARKDOWN_RENDER', {})
        external_dirs = config.get('EXTERNAL_DIRS')
        if external_dirs:
            if isinstance(external_dirs, str):
                allowed_paths.append(os.path.abspath(external_dirs))
                print(f"添加允许的外部目录(字符串): {os.path.abspath(external_dirs)}")
            elif isinstance(external_dirs, (list, tuple)):
                for ext_dir in external_dirs:
                    allowed_paths.append(os.path.abspath(ext_dir))
                    print(f"添加允许的外部目录(列表项): {os.path.abspath(ext_dir)}")
        
        # 添加特定的外部目录
        ext_dir_path = os.path.abspath(r'E:\GitHub\markdown')
        allowed_paths.append(ext_dir_path)
        print(f"添加特定外部目录: {ext_dir_path}")
        
        # 添加当前文件目录
        if os.path.exists(file_path):
            file_dir = os.path.abspath(os.path.dirname(file_path))
            allowed_paths.append(file_dir)
            print(f"添加文件所在目录: {file_dir}")
            
        print(f"允许的路径列表: {allowed_paths}")
            
        path_allowed = False
        for allowed_path in allowed_paths:
            if abs_path.startswith(allowed_path):
                path_allowed = True
                print(f"路径验证成功: {abs_path} 在允许的目录 {allowed_path} 内")
                break
                
        if not path_allowed and allowed_paths:
            error_msg = f"安全警告: 不允许访问系统目录外部的文件"
            print(f"路径验证失败: {error_msg}")
            print(f"  文件路径: {abs_path}")
            print(f"  允许的路径: {allowed_paths}")
            raise ValidationError(error_msg)
                
        path_obj = Path(abs_path)
        if '..' in path_obj.parts:
            error_msg = "安全警告: 检测到目录遍历尝试"
            print(f"路径验证失败: {error_msg}")
            raise ValidationError(error_msg)
        
        print(f"路径验证通过: {abs_path}")    
        return abs_path
    
    @classmethod
    def validate_file(cls, file_path: str) -> str:
        clean_path = cls.sanitize_path(file_path)
        
        cls.validate_extension(clean_path)
        
        cls.validate_mimetype(clean_path)
        
        cls.validate_size(clean_path)
        
        return clean_path 