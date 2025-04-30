from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Document
from .forms import DocumentForm

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