from django.forms import ModelForm
from .models import Assessment, Problem
from django import forms


class CreateAssessmentForm(ModelForm):
    class Meta:
        model = Assessment
        fields = [
            'title'
        ]


class CreateProblemForm(ModelForm):

    class Meta:
        model = Problem
        fields = [
            'description',
            'question'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5})
        }
