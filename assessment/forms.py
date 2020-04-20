from django.forms import ModelForm
from .models import Assessment, Problem, Answer
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


class CreateAnswerForm(ModelForm):
    class Meta:
        model = Answer
        fields = [
            'answer',
        ]


class FindAssessmentForm(forms.Form):
    search = forms.IntegerField(localize=True)


class CarryOutAssessmentForm(forms.Form):
    answer = forms.ChoiceField()

    def __init__(self, choices, **kwargs):
        super(CarryOutAssessmentForm, self).__init__(**kwargs)
        self.fields['answer'].choices = choices


class CheckResultsForm(forms.Form):
    student_id = forms.IntegerField(localize=True)
