import openpyxl
import pandas as pd
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
        form = DocumentForm()
    return render(request, 'excel.html', {
        'form': form
    })


def uploaded(request):
    document = Document.objects.latest('uploaded_at').document
    wb = openpyxl.load_workbook(document)
    ws = wb['Col1']
    excl = []
    columns = []
    for row in ws.iter_rows(values_only = True, min_row = 3, min_col = 2, max_col = 15):
        if row[0] is not None and row[0].isdigit():
            excl.append(row)
        elif row[0] is not None:
            columns = row
    excl = pd.DataFrame(excl)
    excl.columns = columns
    excl = excl.loc[:, [col for col in excl.columns if col is not None]]
    excl.to_csv("excl.csv")
    return render(request, 'uploaded.html', {'document': excl.to_html(justify = 'center', classes = "table table-bordered")})
