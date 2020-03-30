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
    assessments = Assessment.objects.filter(creator__id=user_id).exclude(title='')

    # initialize form
    create_problem_form = CreateProblemForm()
    create_assessment_form = CreateAssessmentForm()

    # create an instance of Assessment
    # without saving it (temporary)
    current_assessment = Assessment.objects.create(
        creator=current_user
    )
    current_assessment.save()
    current_assessment.delete()

    if request.method == 'POST' and \
            current_assessment.title == '' and \
            'create-assessment' in request.POST:
        print('=================================================')
        create_assessment_form = CreateAssessmentForm()
        messages.error(request, 'You have to give your assessment a title before generating it.')

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

    if request.method == 'POST' and \
            'create-assessment' in request.POST and \
            assessment_problems != []:
        create_assessment_form = CreateAssessmentForm(request.POST)
        if create_assessment_form.is_valid():
            for problem in assessment_problems:
                problem.assessment = current_assessment
            title = create_assessment_form.cleaned_data['title']
            if title != '':
                current_assessment = Assessment.objects.create(
                    creator=current_user,
                    title=title,
                )
                current_assessment.save()
                assessment_problems.clear()

    # context for home view
    user_assessments = Assessment.objects.filter(creator=User.objects.get(id=user_id))
    context = {
        'create_assessment_form': create_assessment_form,
        'create_problem_form': create_problem_form,
        'user_assessments': user_assessments,
        'assessment_problems': assessment_problems,
        'assessments': assessments,
    }
    return render(request, template_name, context)
