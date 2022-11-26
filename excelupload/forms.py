from django import forms

from .models import Document


class DocumentForm(forms.ModelForm):
    degree = forms.ChoiceField(choices = Document.degree_choices, label = 'Course')

    class Meta:
        model = Document
        fields = ('student_number', 'degree', 'boot_math', 'boot_com', 'paper_test', 'document')
        labels = {
            'student_number': 'Student Number',
            'degree'        : 'Course',
            'boot_math'     : 'Passed Mathematics/Statistics',
            'boot_com'      : 'Passed Computing',
            'paper_test'    : 'Passed Qualification Exam',
            'document'      : 'Upload Excel',
        }
        widgets = {
            'boot_math' : forms.CheckboxInput(),
            'boot_com'  : forms.CheckboxInput(),
            'paper_test': forms.CheckboxInput()
        }
        help_texts = {
            'student_number': 'ex. 2022-12345',
        }
