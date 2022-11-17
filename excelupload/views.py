from django.shortcuts import redirect, render

from excelupload.forms import DocumentForm
from excelupload.models import Document
from django.shortcuts import redirect, render

from excelupload.forms import DocumentForm
from excelupload.models import Document


# Create your views here.
def excel_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('uploaded')
        else:
            raise Exception()
    else:
        form = DocumentForm()
    return render(request, 'excel.html', {
        'form': form
    })


def uploaded(request):
    document = Document.objects.latest('uploaded_at').document
    data = (document.read())
    return render(request, 'uploaded.html', {'document': data})
