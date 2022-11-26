# Create your views here.
import openpyxl
import pandas as pd
from django.shortcuts import render

from check.models import CheckCourse
from excelupload.models import Document


def uploaded(request):
    document_model = Document.objects.latest('uploaded_at')
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

    excl_changed = changer(input_df = excl, admission = admission_year)
    return render(request, 'uploaded.html', {'document': excl_changed.to_html(justify = 'center', classes = "table alt")})


def changer(input_df: pd.DataFrame, admission = 2022) -> pd.DataFrame:
    size_row = len(input_df)
    info = []
    dic_year = {2020: 'yr_20', 2021: 'yr_21', 2022: 'yr_22'}
    chck_col = dic_year[admission]
    course = CheckCourse.objects.all()
    for i in range(size_row):
        one_row = list(input_df.iloc[i, :])
        if pd.notna(one_row[0]):  # 그 로우의 1번째 인덱스가 수업연도여야 볼거야.
            try:
                int(one_row[0])
            except ValueError:
                continue
            # 유의미한 row 필터링 완료.
            new_info = [one_row[0], one_row[1], one_row[2]]

            try:
                course_key = course.get(cid = one_row[2]).cid_int  # 교과목 번호

            except CheckCourse.DoesNotExist:  # 처음보는 교과목번호에 대해서 처리 (해외연수등)
                if one_row[4] == 3 or one_row[4] == '3':
                    course_key = 10003
                elif one_row[4] == 2 or one_row[4] == '2':
                    course_key = 10002
                else:
                    course_key = 10001
            new_info.append(course_key)

            new_info.append(one_row[11])  # 과목명
            new_info.append(int(one_row[4]))  # 학점
            new_info.append(one_row[5])  # 성적
            new_info.append(course.filter(cid_int = course_key).values_list(chck_col, flat = True)[0])  # 교과구분
            new_info.append(one_row[8])  # 재수강
            info.append(new_info)
    grade = pd.DataFrame(info)
    grade.columns = ['year', 'semester', 'cid', 'cid_int', 'cname', 'crd', 'gpa', 'gbn', 're']
    return grade


def delete_redundant():
    pass


def please_graduate(document_model: Document):
    document = document_model.document
    admission_year = int(document_model.student_number[:4])
    wb = openpyxl.load_workbook(document)
    ws = wb['Col1']
    df = []
    columns = []
    for row in ws.iter_rows(values_only = True, min_row = 3, min_col = 2, max_col = 15):
        if row[0] is not None and row[0].isdigit():
            df.append(row)
        elif row[0] is not None:
            columns = row
    df = pd.DataFrame(df)
    df.columns = columns
    df = df.loc[:, [col for col in df.columns if col is not None]]

    df_changed = changer(input_df = df, admission = admission_year)

    pass
