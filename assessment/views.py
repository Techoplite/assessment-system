from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CreateAssessmentForm, CreateProblemForm, CreateAnswerForm
from .models import Assessment, Problem, Answer
from accounts.models import User
from core.views import home


def create_assessment(request):
    # Fetch the current user.
    user_id = request.user.id
    current_user = User.objects.get(id=user_id)

    # Initialize forms.
    create_problem_form = CreateProblemForm()
    create_assessment_form = CreateAssessmentForm()
    create_answer_form = CreateAnswerForm()

    # Create a temporary Assessment
    # if one does not exists yet.
    first_access_temporary_assessment = Assessment.objects.filter(title='')

    if not first_access_temporary_assessment:
        temporary_assessment = Assessment.objects.create(
            creator=current_user
        )
        temporary_assessment.save()
        Problem.objects.all().delete()

    temporary_assessment = Assessment.objects.get(title='')

    # Fetch temporary assessment problems.
    assessment_problems = Problem.objects.filter(creator=current_user, assessment=temporary_assessment)

    # Check if a problem is finished.
    problem_to_be_answered = assessment_problems.last()
    problem_finished = None
    problem_answers = None

    is_problem_finished = Answer.objects.filter(problem_finished=True)

    print('THIS IS THE OUTER ANSWERS: ' + str(Answer.objects.all()))

    if is_problem_finished:
        problem_finished = Answer.objects.get(problem_finished=True).question
        print(f'THIS PROBLEM IS FINISHED {problem_finished} with last answer {Answer.objects.get(problem_finished=True)}')
        last_answer = Answer.objects.get(problem_finished=True)
        last_answer.problem_finished = False
        last_answer.save()
    if assessment_problems and problem_finished:
        problem_to_be_answered = None
    elif assessment_problems and not problem_finished:
        problem_to_be_answered = assessment_problems.last()

    # Fetch the answers related to the current problem.
    for problem in assessment_problems:
        problem_answers = Answer.objects.filter(creator=current_user, question=problem)

    # Successfully create answer.
    if request.method == 'POST' and 'create-answer' in request.POST:
        create_answer_form = CreateAnswerForm(request.POST)
        if create_answer_form.is_valid():
            answer = create_answer_form.cleaned_data['answer']
            new_answer = Answer.objects.create(
                creator=current_user,
                question=problem_to_be_answered,
                answer=answer
            )
            new_answer.save()
            return redirect(create_assessment)

    # All answers to a problem
    # have been created. Finish the problem.
    if request.method == 'POST' and 'problem-finished' in request.POST:
        create_answer_form = CreateAnswerForm(request.POST)
        if create_answer_form.is_valid():
            print('THE CODE REACHED THIS POINT')
            answer = create_answer_form.cleaned_data['answer']
            new_answer = Answer.objects.create(
                creator=current_user,
                question=problem_to_be_answered,
                answer=answer,
                problem_finished=True
            )
            new_answer.save()
            print(f'THIS IS LAST ANSWER FOR PROBLEM {new_answer.question} {new_answer}')
            print('THESE ALE ALL THE ANSWERS : ' + str(Answer.objects.all()))
            return redirect(create_assessment)

    # Reset assessment.
    if request.method == 'POST' and 'reset-assessment' in request.POST:
        Problem.objects.filter(assessment=temporary_assessment).delete()

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
        return redirect(create_assessment)



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

    # Fetch temporary assessment problems.
    assessment_problems = Problem.objects.filter(creator=current_user, assessment=temporary_assessment)

    user_assessments = Assessment.objects.filter(creator=current_user).exclude(title='')

    template_name = 'create_assessment.html'

    context = {
        'create_assessment_form': create_assessment_form,
        'create_problem_form': create_problem_form,
        'create_answer_form': create_answer_form,
        'assessment_problems': assessment_problems,
        'user_assessments': user_assessments,
        'problem_answers': problem_answers,
        'problem_to_be_answered': problem_to_be_answered,
    }
    return render(request, template_name, context)


def delete_assessment(request):
    # Cancel all unassigned problems.
    temporary_assessment = Assessment.objects.get(title='')
    unassigned_problems = Problem.objects.filter(assessment=temporary_assessment)
    unassigned_problems.delete()

    # Fetch user id.
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
    # Cancel all unassigned problems.
    temporary_assessment = Assessment.objects.get(title='')
    unassigned_problems = Problem.objects.filter(assessment=temporary_assessment)
    unassigned_problems.delete()

    # Fetch user id.
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

    # Fetch user id
    user_id = current_assessment.creator.id

    # Fetch the current user's assessments.
    user_assessments = Assessment.objects.filter(creator__id=user_id).exclude(title='')

    # Initialize forms.
    edit_problem_form = CreateProblemForm()

    # Successfully edit the problem.
    if request.method == 'POST' and 'edit-problem' in request.POST:
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
