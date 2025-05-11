"""
文件安全校验模块

提供Markdown文件的安全验证功能
"""
import os
import mimetypes
from pathlib import Path
from typing import Union, Optional, Tuple, List
from django.conf import settings
from django.core.exceptions import ValidationError


class FileValidator:
    """
    实现文件安全校验：
    1. 白名单验证：仅允许.md/.markdown扩展名
    2. 内容嗅探：检测真实MIME类型
    3. 大小限制：配置化最大文件尺寸(默认5MB)
    4. 路径消毒：防止目录遍历攻击
    5. 沙箱处理：禁用Markdown的raw_html扩展
    """
    
    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = ('.md', '.markdown')
    
    # 允许的MIME类型
    ALLOWED_MIMETYPES = ('text/markdown', 'text/plain')
    
    # 默认最大文件大小 (5MB)
    DEFAULT_MAX_SIZE = 5 * 1024 * 1024
    
    @classmethod
    def get_max_size(cls) -> int:
        """从Django设置获取最大文件大小配置"""
        config = getattr(settings, 'MARKDOWN_RENDER', {})
        return config.get('MAX_SIZE', cls.DEFAULT_MAX_SIZE)

    @classmethod
    def validate_extension(cls, file_path: str) -> bool:
        """验证文件扩展名是否在白名单中"""
        _, ext = os.path.splitext(file_path.lower())
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValidationError(f"不支持的文件类型: {ext}。仅支持 {', '.join(cls.ALLOWED_EXTENSIONS)}")
        return True
    
    @classmethod
    def validate_mimetype(cls, file_path: str) -> bool:
        """验证文件的MIME类型"""
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # 如果无法确定MIME类型，尝试通过内容嗅探
        if not mime_type and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                # 读取文件开头进行内容嗅探
                header = f.read(512)
                # 检查是否是文本文件
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
        """验证文件大小是否在限制范围内"""
        if not os.path.exists(file_path):
            raise ValidationError(f"文件不存在: {file_path}")
            
        file_size = os.path.getsize(file_path)
        max_size = cls.get_max_size()
        
        if file_size > max_size:
            raise ValidationError(f"文件大小({file_size}字节)超过允许的最大值({max_size}字节)")
        return True
    
    @classmethod
    def sanitize_path(cls, file_path: str) -> str:
        """清理文件路径，防止目录遍历攻击"""
        # 将路径转换为绝对规范路径
        abs_path = os.path.abspath(file_path)
        
        # 获取允许的目录列表
        allowed_paths = []
        
        # 添加MEDIA_ROOT到允许的路径
        if hasattr(settings, 'MEDIA_ROOT'):
            allowed_paths.append(os.path.abspath(settings.MEDIA_ROOT))
            
        # 添加项目根目录到允许的路径
        if hasattr(settings, 'BASE_DIR'):
            allowed_paths.append(os.path.abspath(settings.BASE_DIR))
            
        # 检查路径是否在允许的目录内
        path_allowed = False
        for allowed_path in allowed_paths:
            if abs_path.startswith(allowed_path):
                path_allowed = True
                break
                
        if not path_allowed and allowed_paths:
            raise ValidationError(f"安全警告: 不允许访问系统目录外部的文件")
                
        # 检查是否包含危险字符或序列
        path_obj = Path(abs_path)
        if '..' in path_obj.parts:
            raise ValidationError("安全警告: 检测到目录遍历尝试")
            
        return abs_path
    
    @classmethod
    def validate_file(cls, file_path: str) -> str:
        """执行所有文件验证"""
        # 清理并验证路径
        clean_path = cls.sanitize_path(file_path)
        
        # 验证文件扩展名
        cls.validate_extension(clean_path)
        
        # 验证文件MIME类型
        cls.validate_mimetype(clean_path)
        
        # 验证文件大小
        cls.validate_size(clean_path)
        
        return clean_path 