from django.db import models
from django.contrib.auth.models import User
import os

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def is_markdown(self):
        """检查文件是否为Markdown文件"""
        _, ext = os.path.splitext(self.file.name)
        return ext.lower() in ['.md', '.markdown']
        
    def get_file_type(self):
        """获取文件类型"""
        _, ext = os.path.splitext(self.file.name)
        ext = ext.lower()
        
        if ext in ['.md', '.markdown']:
            return 'markdown'
        elif ext in ['.txt', '.log', '.ini', '.conf', '.cfg', '.properties']:
            return 'text'
        elif ext in ['.html', '.htm', '.xml', '.json', '.yaml', '.yml', '.css', '.js']:
            return 'code'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']:
            return 'image'
        elif ext in ['.pdf']:
            return 'pdf'
        elif ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
            return 'office'
        else:
            return 'other'