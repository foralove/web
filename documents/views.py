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
            document = get_object_or_404(Document, id=doc_id)
            
            if document.owner != request.user:
                return render(request, 'documents/document_view.html', {
                    'document': {'title': '访问被拒绝'},
                    'html_content': "<div class='alert alert-danger'>您没有权限查看此文档。</div>",
                    'is_markdown': False,
                })
            
            if not os.path.exists(document.file.path):
                html_content = "<div class='alert alert-danger'>文件不存在或已被删除。</div>"
                return render(request, 'documents/document_view.html', {
                    'document': document,
                    'html_content': html_content,
                    'is_markdown': False,
                })
            
            file_type = document.get_file_type()
            file_path = document.file.path
            
            if file_type == 'markdown':
                html_content = render_markdown(file_path)
                is_preview = True
            elif file_type == 'text' or file_type == 'code':
                try:
                    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
                    content = None
                    
                    for encoding in encodings:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                content = f.read()
                            if '\ufffd' not in content[:100]:
                                break
                        except UnicodeDecodeError:
                            continue
                    
                    if content is None or '\ufffd' in content[:100]:
                        import chardet
                        with open(file_path, 'rb') as f:
                            raw_content = f.read()
                            detected = chardet.detect(raw_content)
                            encoding = detected['encoding'] or 'utf-8'
                            content = raw_content.decode(encoding)
                    
                    from django.utils.html import escape
                    content = escape(content)
                    
                    if file_type == 'code':
                        import pygments
                        from pygments.lexers import get_lexer_for_filename
                        from pygments.formatters import HtmlFormatter
                        
                        try:
                            lexer = get_lexer_for_filename(file_path)
                            formatter = HtmlFormatter(linenos=True, cssclass="highlight")
                            highlighted = pygments.highlight(content, lexer, formatter)
                            html_content = f"""
                            <div class="code-container">
                                <style>{HtmlFormatter().get_style_defs('.highlight')}</style>
                                {highlighted}
                            </div>
                            """
                        except Exception:
                            html_content = f'<pre class="text-content">{content}</pre>'
                    else:
                        html_content = f'<pre class="text-content">{content}</pre>'
                    
                    is_preview = True
                except Exception as e:
                    html_content = f"""
                    <div class='alert alert-warning'>
                        <h4>无法预览文本内容</h4>
                        <p>{str(e)}</p>
                    </div>
                    """
                    is_preview = False
            elif file_type == 'image':
                file_url = document.file.url
                html_content = f"""
                <div class="image-container text-center">
                    <img src="{file_url}" class="img-fluid" alt="{document.title}">
                </div>
                """
                is_preview = True
            elif file_type == 'pdf':
                file_url = document.file.url
                html_content = f"""
                <div class="pdf-container">
                    <embed src="{file_url}" type="application/pdf" width="100%" height="600px">
                    <p class="mt-2">如果您的浏览器无法预览PDF，请<a href="{file_url}" target="_blank">点击此处</a>下载查看。</p>
                </div>
                """
                is_preview = True
            else:
                html_content = "<div class='alert alert-info'>此文件类型无法在线预览，请下载后查看。</div>"
                is_preview = False
            
            return render(request, 'documents/document_view.html', {
                'document': document,
                'html_content': html_content,
                'is_markdown': is_preview,
                'file_type': file_type,
            })
        except (Document.DoesNotExist, django.http.Http404):
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
    
@login_required
def delete_document(request, doc_id):
    try:
        document = get_object_or_404(Document, id=doc_id)
        
        if document.owner != request.user:
            return redirect('document_list')
        
        document_title = document.title
        
        document.delete()
        
        return redirect('document_list')
    except Exception as e:
        import traceback
        error_message = f"""
        <div class='alert alert-danger'>
            <h4>删除文档时发生错误</h4>
            <p>{str(e)}</p>
            <pre>{traceback.format_exc()}</pre>
        </div>
        """
        return render(request, 'documents/error.html', {
            'title': '删除错误',
            'error_message': error_message,
        })
    
@login_required
def external_markdown_view(request, file_name=None):
    if not file_name:
        file_name = 'test_document.md'
    
    file_path = os.path.join(r'E:\GitHub\markdown', file_name)
    
    print(f"渲染外部Markdown文件: {file_path}")
    print(f"文件是否存在: {os.path.exists(file_path)}")
    
    md_dir = r'E:\GitHub\markdown'
    images_dir = os.path.join(md_dir, 'images')
    print(f"Markdown目录是否存在: {os.path.exists(md_dir)}")
    print(f"images目录是否存在: {os.path.exists(images_dir)}")
    
    if os.path.exists(images_dir):
        try:
            import glob
            image_files = glob.glob(os.path.join(images_dir, '*.*'))
            print(f"images目录中的文件: {image_files}")
        except Exception as e:
            print(f"列出images目录内容时出错: {str(e)}")
    
    if not os.path.exists(file_path):
        html_content = f"<div class='alert alert-danger'>文件 {file_name} 不存在或不可访问。</div>"
        return render(request, 'documents/document_view.html', {
            'document': {'title': '文件不存在'},
            'html_content': html_content,
            'is_markdown': False,
        })
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
            print(f"Markdown文件内容长度: {len(raw_content)} 字节")
            print(f"Markdown文件前100字符: {raw_content[:100].replace('\n', '\\n')}")
            
            if '![' in raw_content:
                print(f"文件包含图片引用，总数: {raw_content.count('![')}")
                import re
                img_matches = re.findall(r'!\[(.*?)\]\s*\((.*?)\)', raw_content)
                for i, (alt, src) in enumerate(img_matches, 1):
                    print(f"图片 {i}: alt='{alt}', src='{src.strip()}'")
                    
                    img_path = src.strip()
                    if img_path.startswith('./'):
                        rel_path = os.path.join(os.path.dirname(file_path), img_path[2:])
                        if os.path.exists(rel_path):
                            print(f"  - 图片文件存在于相对路径: {rel_path}")
                        else:
                            alt_path = os.path.join(md_dir, img_path[2:])
                            if os.path.exists(alt_path):
                                print(f"  - 图片文件存在于替代路径: {alt_path}")
                            else:
                                print(f"  - 图片文件不存在!")
                    elif os.path.isabs(img_path):
                        if os.path.exists(img_path):
                            print(f"  - 图片文件存在于绝对路径: {img_path}")
                        else:
                            print(f"  - 图片文件不存在!")
                    else:
                        rel_path = os.path.join(os.path.dirname(file_path), img_path)
                        if os.path.exists(rel_path):
                            print(f"  - 图片文件存在于相对路径: {rel_path}")
                        else:
                            alt_path = os.path.join(md_dir, img_path)
                            if os.path.exists(alt_path):
                                print(f"  - 图片文件存在于替代路径: {alt_path}")
                            else:
                                print(f"  - 图片文件不存在!")
            
            link_matches = re.findall(r'\[(.*?)\]\s*\((.*?)\)', raw_content)
            if link_matches:
                print(f"文件包含超链接，总数: {len(link_matches)}")
                for i, (text, url) in enumerate(link_matches, 1):
                    if not text.startswith('!'):
                        print(f"超链接 {i}: text='{text}', url='{url.strip()}'")
        
        from markdown_renderer.utils import render_markdown
        html_content = render_markdown(file_path)
        
        img_count = html_content.count('<img')
        a_count = html_content.count('<a href')
        print(f"渲染后HTML包含 {img_count} 个img标签, {a_count} 个a标签")
        
        return render(request, 'documents/document_view.html', {
            'document': {'title': f'外部文件: {file_name}'},
            'html_content': html_content,
            'is_markdown': True,
            'debug_info': {
                'file_path': file_path,
                'md_dir_exists': os.path.exists(md_dir),
                'images_dir_exists': os.path.exists(images_dir),
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'img_count': img_count,
                'link_count': a_count
            }
        })
    except Exception as e:
        import traceback
        print(f"渲染错误: {str(e)}")
        print(traceback.format_exc())
        html_content = f"""
        <div class='alert alert-danger'>
            <h4>渲染错误</h4>
            <p>文件: {file_path}</p>
            <p>错误: {str(e)}</p>
            <pre>{traceback.format_exc()}</pre>
        </div>
        """
        return render(request, 'documents/document_view.html', {
            'document': {'title': '渲染错误'},
            'html_content': html_content,
            'is_markdown': False,
        })