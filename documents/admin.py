from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'uploaded_at')
    list_filter = ('owner', 'uploaded_at')
    search_fields = ('title',) 