from django.shortcuts import render
from assessment.models import Assessment


def home(request):
    template_name = 'home.html'
    assessments = Assessment.objects.all()
    context = {
        'assessments': assessments,
    }
    return render(request, template_name, context)

