import pandas as pd
from django.db.models import Sum

from check.models import CheckCourse


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


def delete_redundant(enrollments):
    enrollments_filtered = enrollments.exclude(gpa__in = ['F', 'U'])
    enrollments_mldl1 = enrollments_filtered.filter(cid_int__in = [9563, 9564])
    enrollments_bkms1 = enrollments_filtered.filter(cid_int__in = [9562, 9598])
    enrollments_computing1 = enrollments_filtered.filter(cid_int__in = [9596, 9564])
    enrollments_computing2 = enrollments_filtered.filter(cid_int__in = [9595, 9582])
    enrollments_redundancy = [enrollments_mldl1, enrollments_bkms1, enrollments_computing1, enrollments_computing2]

    for enrollment_re in enrollments_redundancy:
        if enrollment_re.count() > 1:
            if enrollment_re.filter(re = True).count() == 1:
                enrollments_filtered = enrollments_filtered.exclude(enrollment_re.filter(re = False))
            elif enrollment_re.filter(re = True).count() > 1:
                enrollments_filtered = enrollments_filtered.exclude(enrollment_re.filter(re = True).order_by('-gpa'))
    return enrollments_filtered


def can_graduate(enrollments, documents):
    grade_alph_float = {'A+': 4.3, 'A0': 4., 'A-': 3.7, 'B+': 3.3, 'B0': 3, 'B-': 2.7, 'C+': 2.3, 'C0': 2., 'C-': 1.7, 'D+': 1.3, 'D0': 1., 'D-': 0.7, 'F': 0}

    basic_math_checker, basic_computing = documents.boot_math, documents.boot_com
    if not basic_math_checker:
        basic_math_checker = enrollments.filter(cid_int__in = [9599, 9576, 9565], gpa__in = ['A+', 'A0', 'A-', 'B+', 'B0']).count() > 0

    if not basic_computing:
        basic_computing = enrollments.filter(cid_int__in = [9597, 9577, 9566], gpa__in = ['A+', 'A0', 'A-', 'B+', 'B0']).count() > 0

    qe_passed = documents.paper_test and basic_math_checker and basic_computing

    admission_year = int(documents.student_number[:4])
    print_list = []
    checkers = []

    crd_sum = 0

    if admission_year == 2020:
        # 여러가지 졸업요건을위한 변수들
        checker_paper = True  # 논문
        valid_paper = None
        count_paper = enrollments.filter(gbn = '논문').count()

        checker_calculate = True  # 계산
        count_calculate = enrollments.filter(gbn = '계산').count()

        check_seminar = True  # 세미나
        count_seminar = 0

        check_non_seminar = True  # 공통-세미나
        count_non_seminar = 0

        checker_select1 = True  # 분석
        count_select1 = enrollments.filter(gbn = '분석').count()

        checker_select2 = True  # 응용
        count_select2 = enrollments.filter(gbn = '응용').count()

        ###공통 판단 : 공통에서 세미나와 그 외 과목을 나눠서 생각해야 한다.
        enrollment_common = enrollments.filter(gbn = '공통')
        count_seminar = enrollment_common.filter(cid_int__in = [9579, 9568]).count()
        count_non_seminar = enrollment_common.count() - count_seminar  # 세미나 제외

        credit_common = enrollment_common.exclude(cid_int = 9571).aggregate(Sum('crd'))['crd__sum']

        check_seminar = (count_seminar >= 2)
        check_non_seminar = (count_non_seminar > 0)

        if documents.degree == '석사':
            if count_paper == 0:  # 논문과목을 한번도 안들었다면.
                checker_paper = False
            valid_paper = min(count_paper, 2)
            if count_calculate < 3:  # 계산과목을 3번 미만 들었다면
                checker_calculate = False
            if count_select1 + count_select2 == 0:
                checker_select1 = False
                checker_select2 = False
        else:
            if count_paper < 2:  # 논문과목을 두번 미만으로 들었다면.
                checker_paper = False
            valid_paper = min(count_paper, 4)
            if count_calculate < 5:  # 계산과목을 5번 미만 들었다면
                checker_calculate = False

            if count_select1 < 2:  # 분석을 2번 미만 들었다면
                checker_select1 = False

            if count_select2 < 2:  # 응용을 2번 미만 들었다면
                checker_select2 = False

        # crd_sum = credit_common + count_math*3 + count_calculate*3
        # crd_sum += enrollments.filter(gbn = '응용').count()*3  # 응용과목 수강 횟수 * 학점(3)
        crd_basic = enrollments.filter(gbn = '기초').exclude(cid_int__in = [9599, 9576, 9565] + [9597, 9577, 9566])
        try:
            if crd_basic.count() > 0:
                crd_sum += crd_basic.aggregate(Sum('crd'))['crd__sum']
            crd_sum += valid_paper*3  # 유효 논문연구강의 수강 횟수 * 학점(3)
            crd_sum += count_calculate*3  # 계산과목 수강 횟수 * 학점(3)
            crd_sum += count_select1*3  # 분석과목 수강 횟수 * 학점(3)
            crd_sum += count_select2*3  # 응용과목 수강 횟수 * 학점(3)
            crd_sum += credit_common
        except TypeError:
            crd_sum = 0

        print_list = ['논문 연구 검사', '계산 과목 검사', '공통 과목 검사(세미나 제외)', '세미나 검사', '분석 과목 검사', '응용 과목 검사']
        checkers = [checker_paper,
                    checker_calculate,
                    check_non_seminar,
                    check_seminar,
                    checker_select1,
                    checker_select2]
    elif admission_year == 2021:
        # 여러가지 졸업요건을위한 변수들
        checker_paper = True  # 논문
        valid_paper = 0
        count_paper = 0

        checker_calculate = True  # 계산
        count_calculate = enrollments.filter(gbn = '계산').count()

        checker_math = True  # 수학 및 통계
        count_math = enrollments.filter(gbn = '수학 및 통계').count()

        checker_seminar = True  # 세미나
        count_seminar = 0

        checker_non_seminar = True  # 공통-세미나
        count_non_seminar = 0

        checker_common = True  # 공통과목 학점기준
        credit_common = 0  # 세미나를 포함한 공통과목 학점 총량

        ###공통 판단 : 공통에서 세미나와 그 외 과목을 나눠서 생각해야 한다.
        enrollment_common = enrollments.filter(gbn = '공통')
        count_seminar = enrollment_common.filter(cid_int__in = [9579, 9568]).count()
        count_paper = enrollment_common.filter(cid_int = 9571).count()  # 논문은 수료에 불포함
        count_non_seminar = enrollment_common.count() - count_seminar - count_paper  # 논문과 세미나 제외

        credit_common = enrollment_common.exclude(cid_int = 9571).aggregate(Sum('crd'))['crd__sum']

        check_seminar = (count_seminar >= 2)
        check_non_seminar = (count_non_seminar > 0)
        checker_common = (credit_common >= 6)

        if documents.degree == '석사':
            checker_paper = (count_paper != 0)
            valid_paper = min(count_paper, 2)
            if count_math + count_calculate < 5:
                checker_calculate = False
                checker_math = False
        else:
            checker_paper = (count_paper >= 2)
            valid_paper = min(count_paper, 4)
            if count_math + count_calculate < 6:
                checker_calculate = False
                checker_math = False
        try:
            crd_sum = credit_common + count_math*3 + count_calculate*3
            crd_sum += enrollments.filter(gbn = '응용').count()*3  # 응용과목 수강 횟수 * 학점(3)
            crd_basic = enrollments.filter(gbn = '기초').exclude(cid_int__in = [9599, 9576, 9565] + [9597, 9577, 9566])
            if crd_basic.count() > 0:
                crd_sum += crd_basic.aggregate(Sum('crd'))['crd__sum']
        except TypeError:
            crd_sum = 0

        print_list = ['논문 연구 검사', '세미나 검사', '공통 과목 검사(세미나 제외)', '공통 과목 학점 검사', '수학 및 통계 과목 검사']
        checkers = [checker_paper, checker_seminar, checker_non_seminar, checker_common, checker_math]
    elif admission_year == 2022:
        checker_ms = True
        checker_select = True

        checker_paper = True  # 논문(선택과목에 포함됨) -> 박사나 석박통합만 학점으로 인정된다.
        valid_paper = 0
        count_paper = 0
        credit_paper = 0
        credit_non_paper = 0
        crd_sum = 0

        checker_common = True  # 공통과목 학점기준
        credit_common = 0

        checker_seminar = True  # 세미나
        count_seminar = 0

        checker_non_seminar = True  # 공통-세미나
        count_non_seminar = 0

        enrollments_mldl1 = enrollments.filter(cid_int__in = [9563, 9594]).count() > 0  # 석사전필
        enrollments_mldl2 = enrollments.filter(cid_int = 9591).count() > 0  # 석사전필
        enrollments_bkms1 = enrollments.filter(cid_int__in = [9562, 9598]).count() > 0  # 석사전필
        enrollments_bkms2 = enrollments.filter(cid_int = 9592).count() > 0  # 석사전필
        enrollments_com1 = enrollments.filter(cid_int__in = [9596, 9564]).count() > 0  # 석사전필
        enrollments_com2 = enrollments.filter(cid_int__in = [9595, 9582]).count() > 0  # 석사전필
        enrollments_proj = enrollments.filter(cid_int = 9602).count() > 0  # 석사전필

        enrollments_mandatory = [enrollments_mldl1, enrollments_mldl2, enrollments_bkms1, enrollments_bkms2, enrollments_com1, enrollments_com2, enrollments_proj]

        credit_mandatory = enrollments.filter(gbn = '석사전필').aggregate(Sum('crd'))['crd__sum']

        if False in enrollments_mandatory:
            checker_ms = False

        # 공통
        enrollment_common = enrollments.filter(gbn = '공통')
        count_seminar = enrollment_common.filter(cid_int__in = [9579, 9568]).count()
        count_non_seminar = enrollment_common.count() - count_seminar  # 세미나 제외
        credit_common = enrollment_common.aggregate(Sum('crd'))['crd__sum']

        if count_seminar < 3:  # 세미나 세번 미만으로 들었다면.
            checker_seminar = False

        enrollment_select = enrollments.filter(gbn = '선택')
        count_paper = enrollment_select.filter(cid_int = 9571).count()
        credit_non_paper = enrollment_select.exclude(cid_int = 9571).aggregate(Sum('crd'))['crd__sum']
        if credit_non_paper is None:
            credit_non_paper = 0

        if documents.degree == '석사':  # 석사라면
            if count_paper == 0:  # 논문과목을 한번도 안들었다면.
                checker_paper = False
            valid_paper = min(count_paper, 2)  # 2과목을 넘어서면 의미없다.
            credit_paper = valid_paper*3

            if credit_non_paper == 0:  # 선택과목(논문과목 제외) 1과목을 들어야한다.
                checker_select = False

        else:  # 박사나 석박통합이라면
            if count_paper < 2:  # 논문과목을 두번 미만으로 들었다면.
                checker_paper = False
            valid_paper = min(count_paper, 4)  # 4과목을 넘어서면 의미없다.
            credit_paper = valid_paper*3

            if count_non_seminar == 0:  # 세미나가 아닌 공통과목을 한번도 안들었다면
                checker_non_seminar = False

            if credit_common < 6:  # 공통과목의 학점이 6을 못넘는다면
                checker_non_seminar = False

            if credit_paper + credit_non_paper < 18:
                checker_select = False
        try:
            crd_sum = credit_common + credit_paper + credit_non_paper + credit_mandatory
        except TypeError:
            crd_sum = 0
        print_list = ['석사 전필과목 검사', '선택 과목 검사', '논문 연구 검사', '공통 과목 검사', '세미나 검사', '공통 과목 검사(세미나 제외)']
        checkers = [checker_ms, checker_select, checker_paper, checker_common, checker_seminar, checker_non_seminar]

    credit_checker = True

    if documents.degree == '석사':
        if crd_sum < 24:
            credit_checker = False
    elif documents.degree == '박사':
        if crd_sum < 36:
            credit_checker = False
    else:
        if crd_sum < 60:
            credit_checker = False

    print_list.append('수료 학점 검사')
    checkers.append(credit_checker)
    print_list.append('수료 학점')
    checkers.append(crd_sum)
    return {x[0]: x[1] for x in zip(print_list, checkers)}
