from django.shortcuts import render
from assessment.models import Assessment


def home(request):
    template_name = 'home.html'
    user_id = request.user.id
    assessments = Assessment.objects.filter(creator__id=user_id)
    context = {
        'assessments': assessments,
    }
    return render(request, template_name, context)

