from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CreateAssessmentForm, CreateProblemForm
from .models import Assessment, Problem
from accounts.models import User

from core.views import home


def create_assessment(request):
    # Fetch the current user.
    user_id = request.user.id
    current_user = User.objects.get(id=user_id)

    # Initialize forms.
    create_problem_form = CreateProblemForm()
    create_assessment_form = CreateAssessmentForm()

    # Create a temporary Assessment
    # if one does not exists yet.
    first_access_temporary_assessment = Assessment.objects.filter(title='')

    if not first_access_temporary_assessment:
        temporary_assessment = Assessment.objects.create(
            creator=current_user
        )
        temporary_assessment.save()

    temporary_assessment = Assessment.objects.get(title='')

    # Fetch temporary assessment problems.
    assessment_problems = Problem.objects.filter(creator=current_user, assessment=temporary_assessment)
    print('THESE ARE THE ASSESSMENT PROBLEMS WITH GET: ' + str(assessment_problems))

    # Successfully create problem.
    if request.method == 'POST' and 'create-problem' in request.POST:
        create_problem_form = CreateProblemForm(request.POST)
        if create_problem_form.is_valid():
            description = create_problem_form.cleaned_data['description']
            question = create_problem_form.cleaned_data['question']
            new_problem = Problem.objects.create(
                creator=current_user,
                assessment=temporary_assessment,
                description=description,
                question=question,
            )
            new_problem.save()

    # Successfully create an assessment.
    if request.method == 'POST' and \
            'create-assessment' in request.POST and \
            assessment_problems is not None:
        create_assessment_form = CreateAssessmentForm(request.POST)
        if create_assessment_form.is_valid():
            for problem in assessment_problems:
                problem.assessment = temporary_assessment
                problem.save()
            title = create_assessment_form.cleaned_data['title']
            if title != '':
                new_assessment = Assessment.objects.create(
                    creator=current_user,
                    title=title,
                )
                # Fetch temporary problems and assign them
                # to the temporary assessment.
                for problem in assessment_problems:
                    problem.assessment = new_assessment
                    problem.save()
                assessment_problems = Problem.objects.filter(assessment=new_assessment)
                print('THESE ARE THE PROBLEMS WITH SUCCEFFFULL: ' + str(assessment_problems))
                new_assessment.save()
                Problem.objects.filter(assessment=temporary_assessment).delete()
                messages.success(request, f'Assessment "{title}" created successfully.')
                return redirect(home)

    # When trying to generate an assessment with no title
    # a message informs the user that a title must be provided.
    if request.method == 'POST' and \
            temporary_assessment.title == '' and \
            'create-assessment' in request.POST:
        create_assessment_form = CreateAssessmentForm()
        messages.error(request, 'You have to give your assessment a title before generating it.')

    user_assessments = Assessment.objects.filter(creator=current_user).exclude(title='')

    template_name = 'create_assessment.html'

    context = {
        'create_assessment_form': create_assessment_form,
        'create_problem_form': create_problem_form,
        'assessment_problems': assessment_problems,
        'user_assessments': user_assessments,
    }
    return render(request, template_name, context)


def delete_assessment(request):
    # fetch user id
    user_id = request.user.id

    user_assessments = Assessment.objects.filter(creator__id=user_id).exclude(title='')

    template_name = 'delete_assessment.html'

    context = {
        'user_assessments': user_assessments,
    }

    return render(request, template_name, context)


def delete(request, assessment_id):
    assessment = Assessment.objects.get(id=assessment_id)
    Problem.objects.filter(assessment=assessment).delete()
    assessment.delete()
    return redirect(delete_assessment)


def edit_assessment(request):
    user_id = request.user.id

    user_assessments = Assessment.objects.filter(creator__id=user_id).exclude(title='')

    template_name = 'edit_assessment.html'

    context = {
        'user_assessments': user_assessments,
    }

    return render(request, template_name, context)


def edit(request, assessment_id):
    # Fetch the assessment to be edited
    current_assessment = Assessment.objects.get(
        id=assessment_id
    )

    # Fetch the current user.
    user_id = request.user.id
    current_user = User.objects.get(id=user_id)

    # Fetch the current user's assessments.
    user_assessments = Assessment.objects.filter(creator__id=user_id).exclude(title='')

    # Fetch current user's problems.
    assessment_problems = Problem.objects.filter(creator=current_user, assessment=current_assessment)

    # Initialize forms.
    create_problem_form = CreateProblemForm()
    create_assessment_form = CreateAssessmentForm()

    template_name = 'edit_assessment.html'

    context = {
        'create_assessment_form': create_assessment_form,
        'create_problem_form': create_problem_form,
        'assessment_problems': assessment_problems,
        'user_assessments': user_assessments,
        'current_assessment': current_assessment,
    }
    return render(request, template_name, context)


def edit_problem(request, problem_id):

    # Fetch the problem to be edited.
    problem_to_edit = Problem.objects.get(
        id=problem_id
    )

    # Fetch the assessment to be edited
    current_assessment = problem_to_edit.assessment
    print('THIS IS THE ASSESSMENT TO BE EDITED: ' + str(current_assessment))

    # Fetch user id
    user_id = current_assessment.creator.id

    # Fetch the current user's assessments.
    user_assessments = Assessment.objects.filter(creator__id=user_id).exclude(title='')

    # Initialize forms.
    edit_problem_form = CreateProblemForm()

    # Successfully edit the problem.
    if request.method == 'POST' and 'edit-problem' in request.POST:
        print('==============THIS IS THE EDIT BUTTON==================')
        edit_problem_form = CreateProblemForm(request.POST)
        if edit_problem_form.is_valid():
            description = edit_problem_form.cleaned_data['description']
            question = edit_problem_form.cleaned_data['question']
            problem_to_edit.description = description
            problem_to_edit.question = question
            problem_to_edit.save()

    template_name = 'edit_assessment.html'

    context = {
        'edit_problem_form': edit_problem_form,
        'problem_to_edit': problem_to_edit,
        'current_assessment': current_assessment,
        'user_assessments': user_assessments,
    }
    return render(request, template_name, context)
