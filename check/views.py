# Create your views here.

import openpyxl
import pandas as pd
from django.contrib.auth.middleware import get_user
from django.shortcuts import redirect, render

from check.models import Enrollment
from check.utils import can_graduate, changer, delete_redundant
from common.models import Profile
from excelupload.models import Document


def uploaded(request):
    user_id = get_user(request).id
    document_model = Document.objects.filter(user_id = user_id).latest('uploaded_at')
    document = document_model.document
    admission_year = int(document_model.student_number[:4])
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
    up_id = document_model.up_id
    excl_changed = changer(input_df = excl, admission = admission_year)
    enrolled_list = [Enrollment.enrollment_from_df(row, up_id, request) for row in excl_changed.itertuples()]
    Enrollment.objects.bulk_create(enrolled_list)
    Document.objects.filter(user_id = user_id).order_by('uploaded_at')[1].document.delete(save = True)
    return redirect('check:checked')


def check(request):
    user_id = request.user.id
    my_document = Document.objects.filter(user_id = user_id).latest('uploaded_at')
    my_enrollment = Enrollment.objects.filter(up_id = my_document.up_id)
    my_enrollment = delete_redundant(my_enrollment)
    my_enrollment_val = my_enrollment.values_list('year', 'cid', 'cname', 'crd', 'gpa', 'gbn', 're')

    passed = can_graduate(my_enrollment, my_document)

    new_profile = Profile(user = request.user, student_number = my_document.student_number, degree = my_document.degree, passed = passed)
    new_profile.save()
    return render(request, '../templates/check/mypage.html', {'profile': new_profile})


def mypage(request):
    my_profile = {}
    try:
        my_profile = Profile.objects.filter(user_id = request.user.id).latest('uploaded_at')
    except:
        my_profile = ''
    return render(request, '../templates/check/mypage.html', {'profile': my_profile})
