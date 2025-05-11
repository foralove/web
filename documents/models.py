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