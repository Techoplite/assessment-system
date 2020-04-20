from django.shortcuts import render
from assessment.models import Assessment
from accounts.models import User
from assessment.models import Result


def home(request):
    template_name = 'home.html'
    student_results = None

    # Verify that the user is authenticated
    # and fetches the related assessments.
    if request.user.id is not None:
        # Fetch the current user.
        user_id = request.user.id
        current_user = User.objects.get(id=user_id)
        user_assessments = Assessment.objects.filter(creator=current_user).exclude(title='')
        # Fetch student results.
        student_results = Result.objects.filter(student=current_user)

    else:
        user_assessments = None
    context = {
        'user_assessments': user_assessments,
        'student_results': student_results,
    }
    return render(request, template_name, context)

