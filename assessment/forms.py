from django.forms import ModelForm
from .models import Assessment, Problem


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
            'assessment',
            'description',
            'question'
        ]
