from django.shortcuts import render
from .forms import CreateAssessmentForm, CreateProblemForm
from .models import Assessment, Problem
from accounts.models import User


def create_assessment(request):
    template_name = 'create_assessment.html'

    # fetch the current user
    user_id = request.user.id

    # load the forms
    create_assessment_form = CreateAssessmentForm()
    create_problem_form = CreateProblemForm()

    # submit create assessment
    if request.method == 'POST' and 'create-assessment' in request.POST:
        create_assessment_form = CreateAssessmentForm(request.POST)
        if create_assessment_form.is_valid():
            title = create_assessment_form.cleaned_data['title']
            Assessment.objects.create(
                creator=User.objects.get(id=user_id),
                title=title,
            )
    assessments = Assessment.objects.filter(creator__id=user_id)
    problem = Problem.objects.all()

    # submit create problem
    if request.method == 'POST' and 'create-problem' in request.POST:
        print('yey')



    context = {
        'create_assessment_form': create_assessment_form,
        'create_problem_form': create_problem_form,
        'assessments': assessments,
        'problem': problem,
    }
    return render(request, template_name, context)
