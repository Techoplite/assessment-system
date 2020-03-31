from django.shortcuts import render
from assessment.models import Assessment
from accounts.models import User


def home(request):
    template_name = 'home.html'
    # Fetch the current user.
    user_id = request.user.id
    user_assessments = Assessment.objects.filter(creator=User.objects.get(id=user_id))
    context = {
        'user_assessments': user_assessments,
    }
    return render(request, template_name, context)

