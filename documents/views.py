from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Document
from .forms import DocumentForm
from markdown_renderer.utils import render_markdown
import os
import django.http

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.owner = request.user
            document.save()
            return redirect('document_list')
    else:
        form = DocumentForm()
    
    return render(request, 'documents/upload.html', {
        'form': form
    })

class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'
    
    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user).order_by('-uploaded_at')

class SimpleDocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'documents/simple_document_list.html'
    context_object_name = 'documents'
    
    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user).order_by('title')
    
@login_required
def document_view(request, doc_id):
    try:
        try:
            # 尝试获取文档
            try:
                document = Document.objects.get(id=doc_id)
            except Document.DoesNotExist:
                # 文档不存在
                return render(request, 'documents/document_view.html', {
                    'document': {'title': '文档不存在'},
                    'html_content': f"<div class='alert alert-danger'>ID为{doc_id}的文档不存在。</div>",
                    'is_markdown': False,
                })
            
            # 检查是否为当前用户的文档
            if document.owner != request.user:
                return render(request, 'documents/document_view.html', {
                    'document': {'title': '访问被拒绝'},
                    'html_content': "<div class='alert alert-danger'>您没有权限查看此文档。</div>",
                    'is_markdown': False,
                })
            
            # 检查文件是否存在
            if not os.path.exists(document.file.path):
                html_content = "<div class='alert alert-danger'>文件不存在或已被删除。</div>"
                return render(request, 'documents/document_view.html', {
                    'document': document,
                    'html_content': html_content,
                    'is_markdown': False,
                })
            
            # 检查是否为Markdown文件
            if document.is_markdown():
                file_path = document.file.path
                # 渲染Markdown为HTML
                html_content = render_markdown(file_path)
            else:
                # 如果不是Markdown文件，提供一个简单的消息
                html_content = "<div class='alert alert-info'>此文件不是Markdown格式，无法渲染。请下载查看。</div>"
            
            return render(request, 'documents/document_view.html', {
                'document': document,
                'html_content': html_content,
                'is_markdown': document.is_markdown(),
            })
        except (Document.DoesNotExist, django.http.Http404):
            # 文档不存在
            return render(request, 'documents/document_view.html', {
                'document': {'title': '文档不存在'},
                'html_content': f"<div class='alert alert-danger'>ID为{doc_id}的文档不存在。</div>",
                'is_markdown': False,
            })
    except Exception as e:
        import traceback
        error_message = f"""
        <div class='alert alert-danger'>
            <h4>查看文档时发生错误</h4>
            <p>{str(e)}</p>
            <pre>{traceback.format_exc()}</pre>
        </div>
        """
        # 创建一个简单的文档对象用于显示
        document = type('obj', (object,), {
            'title': '文档加载错误',
            'file': None,
            'uploaded_at': None
        })
            
        return render(request, 'documents/document_view.html', {
            'document': document,
            'html_content': error_message,
            'is_markdown': False,
        })
    
    