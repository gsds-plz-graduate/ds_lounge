from django import forms

from .models import Document


class DocumentForm(forms.ModelForm):
    degree = forms.ChoiceField(choices = Document.degree_choices, label = '과정')

    class Meta:
        model = Document
        fields = ('student_number', 'degree', 'document', 'bootMath', 'bootCom', 'paperTest')
        labels = {
            'student_number': '학번',
            'document'      : '성적',
            'degree'        : '과정',
            'bootMath'      : '수학통계 기초 통과',
            'bootCom'       : '컴퓨팅 기초 통과',
            'paperTest'     : '논문자격시험 통과'
        }
        widgets = {
            'bootMath' : forms.CheckboxInput(),
            'bootCom'  : forms.CheckboxInput(),
            'paperTest': forms.CheckboxInput()
        }
        help_texts = {
            'student_number': 'ex. 2022-12345',
        }
