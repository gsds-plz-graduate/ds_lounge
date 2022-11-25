from django import forms

from .models import Document


class DocumentForm(forms.ModelForm):
    degree = forms.ChoiceField(choices = Document.degree_choices, label = 'Course')

    class Meta:
        model = Document
        fields = ('student_number', 'degree', 'bootMath', 'bootCom', 'paperTest', 'document')
        labels = {
            'student_number': 'Student Number',
            'degree'        : 'Course',
            'bootMath'      : 'Passed Mathematics/Statistics',
            'bootCom'       : 'Passed Computing',
            'paperTest'     : 'Passed Qualification Exam',
            'document'      : 'Upload Excel',
        }
        widgets = {
            'bootMath' : forms.CheckboxInput(),
            'bootCom'  : forms.CheckboxInput(),
            'paperTest': forms.CheckboxInput()
        }
        help_texts = {
            'student_number': 'ex. 2022-12345',
        }
