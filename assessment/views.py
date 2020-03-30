from django.contrib import messages
from django.shortcuts import render
from .forms import CreateAssessmentForm, CreateProblemForm
from .models import Assessment, Problem
from accounts.models import User


def create_assessment(request, assessment_problems=[]):
    template_name = 'create_assessment.html'

    # fetch the current user
    user_id = request.user.id
    current_user = User.objects.get(id=user_id)

    # create an instance of Assessment
    # without saving it (temporary)
    current_assessment = Assessment.objects.create(
        creator=current_user
    )

    # load the forms with assessment field choices
    # for CreateProblemForm based on the current user
    create_assessment_form = CreateAssessmentForm()
    create_problem_form = CreateProblemForm()

    # if the assessment is not generated (saved to db)
    # cancel the current (temporary) assessment
    if request.method == 'GET':
        current_assessment.delete()

    if request.method == 'POST' and current_assessment.title == '':
        current_assessment.delete()
        messages.error(request, 'You have to give your assessment a title before generating it.')

    # submit create assessment
    # if request.method == 'POST' and 'create-assessment' in request.POST:

    # submit create problem
    if request.method == 'POST' and 'create-problem' in request.POST:
        create_problem_form = CreateProblemForm(request.POST)
        if create_problem_form.is_valid():
            description = create_problem_form.cleaned_data['description']
            question = create_problem_form.cleaned_data['question']
            new_problem = Problem.objects.create(
                description=description,
                question=question,
            )
            new_problem.save()
            assessment_problems.append(new_problem)
    # context for home view
    user_assessments = Assessment.objects.filter(creator=User.objects.get(id=user_id))
    context = {
        'create_assessment_form': create_assessment_form,
        'create_problem_form': create_problem_form,
        'user_assessments': user_assessments,
        'assessment_problems': assessment_problems,
    }
    return render(request, template_name, context)
