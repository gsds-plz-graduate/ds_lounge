from django import forms

from .models import Document


class DocumentForm(forms.ModelForm):
    degree = forms.ChoiceField(choices = Document.degree_choices, label = '과정')
    class Meta:
        model = Document
        fields = ('student_number', 'degree', 'bootmath', 'bootcom', 'document',)
        labels = {
            'student_number': '학번',
            'document'      : '성적',
            'degree'        : '과정'
        }
        help_texts = {
            'student_number': 'ex. 2022-12345',
        }
