from django.shortcuts import redirect, render

from excelupload.forms import DocumentForm


# Create your views here.

def excel_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('uploaded')
    else:
        form = DocumentForm()
    return render(request, 'excel.html', {
        'form': form
    })