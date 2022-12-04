from django.contrib.auth.middleware import get_user
from django.shortcuts import redirect, render

from excelupload.forms import DocumentForm
from excelupload.models import Document


# Create your views here.

def excel_upload(request):
    if request.method == 'POST':
        form = DocumentForm()
        try:
            user_doc = Document.objects.filter(user = get_user(request).id).last()
            form = DocumentForm(request.POST, request.FILES)
        except Document.DoesNotExist:
            form = DocumentForm(request.POST, request.FILES)
        finally:
            if form.is_valid():
                obj = form.save(commit = False)
                obj.user = get_user(request)
                obj.save()
                return redirect('check:uploaded')
            else:
                raise Exception()
    else:
        form = DocumentForm()
        try:
            user_doc = Document.objects.filter(user = get_user(request).id).last()
            form.fields['student_number'].initial = user_doc.student_number
        except Document.DoesNotExist:
            pass
        finally:
            return render(request, '../templates/excelupload/excel.html', {
                'form': form
            })
