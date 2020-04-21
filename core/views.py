from django.shortcuts import render, redirect
from assessment.models import Assessment
from accounts.models import User
from assessment.models import Result


def home(request):

    # Redirect admin user to the admin page.
    if not request.user.is_anonymous and request.user.is_admin:
        return redirect('/admin/')

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

    welcome_text = 'Welcome to the Assessment System'

    context = {
        'user_assessments': user_assessments,
        'student_results': student_results,
        'welcome_text': welcome_text,
    }
    return render(request, template_name, context)

