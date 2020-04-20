from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CreateAssessmentForm, CreateProblemForm, CreateAnswerForm, FindAssessmentForm, \
    CarryOutAssessmentForm, CheckResultsForm
from .models import Assessment, Problem, Answer, AnswerGiven, Result
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
    problem_to_be_answered = assessment_problems.exclude(is_finished=True).last()
    problem_answers = None

    if assessment_problems and not problem_to_be_answered:
        problem_to_be_answered = None
    elif assessment_problems and problem_to_be_answered:
        problem_to_be_answered = assessment_problems.last()

    # Fetch the answers related to the current problem.
    problems_and_answers = {}
    for problem in assessment_problems:
        problem_answers_list = []
        problem_answers_queryset = Answer.objects.filter(creator=current_user, question=problem)
        for problem_answer_object in problem_answers_queryset:
            problem_answers_list.append(problem_answer_object)
        problems_and_answers.update({problem: problem_answers_list})
    print(problems_and_answers)

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

    # Fetch the user assessment
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
        'problems_and_answers': problems_and_answers,
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

    # Fetch each problem answers nad the correct answer.
    problems_data = {}
    for problem in assessment_problems:
        answers = Answer.objects.filter(creator=current_user, question=problem)
        correct_answer = Answer.objects.filter(question=problem, is_correct_answer=True)

        # Map problems, available answers and correct answers.
        problems_data.update({problem: (answers, correct_answer)})
    print(problems_data)

    # Initialize forms.
    create_problem_form = CreateProblemForm()
    create_assessment_form = CreateAssessmentForm()

    # Fetch any problem with no answer
    # and inform the user.
    problem_with_no_answer = None
    for question in Problem.objects.filter(creator=request.user):
        if len(Answer.objects.filter(creator=request.user, question=question)) == 0:
            problem_with_no_answer = question

    template_name = 'edit_assessment.html'

    context = {
        'create_assessment_form': create_assessment_form,
        'create_problem_form': create_problem_form,
        'assessment_problems': assessment_problems,
        'user_assessments': user_assessments,
        'current_assessment': current_assessment,
        'problem_with_no_answer': problem_with_no_answer,
        'problems_data': problems_data,
    }
    return render(request, template_name, context)


def edit_problem(request, problem_id):
    # Fetch the problem to be edited.
    problem_to_edit = Problem.objects.get(
        id=problem_id
    )

    # Fetch the assessment to be edited
    current_assessment = problem_to_edit.assessment
    assessment_id = current_assessment.id

    # Fetch user id
    user_id = current_assessment.creator.id

    # Fetch the current user's assessments.
    user_assessments = Assessment.objects.filter(creator__id=user_id).exclude(title='')

    # Fetch the answers related to this problem.
    problem_answers_list = []
    problem_answers_queryset = Answer.objects.filter(question=problem_to_edit)
    for problem in problem_answers_queryset:
        problem_answers_list.append(problem)

    # Initialize form.
    description_to_be_edited = problem_to_edit.description
    question_to_be_edited = problem_to_edit.question
    edit_problem_form = CreateProblemForm(
        initial=
        {
            'description': description_to_be_edited,
            'question': question_to_be_edited,
        }
    )
    # Successfully edit the problem.
    if request.method == 'POST' and 'edit-problem' in request.POST:
        edit_problem_form = CreateProblemForm(request.POST)
        if edit_problem_form.is_valid():
            description = edit_problem_form.cleaned_data['description']
            question = edit_problem_form.cleaned_data['question']
            problem_to_edit.description = description
            problem_to_edit.question = question
            problem_to_edit.save()
            messages.success(request, f'Question "{question}" edited successfully.')
            return redirect(edit, assessment_id=current_assessment.id)

    template_name = 'edit_assessment.html'

    context = {
        'edit_problem_form': edit_problem_form,
        'problem_to_edit': problem_to_edit,
        'current_assessment': current_assessment,
        'user_assessments': user_assessments,
        'problem_answers_queryset': problem_answers_queryset,
        'problem_id': problem_id,
        'assessment_id': assessment_id,
    }
    return render(request, template_name, context)


def edit_answer(request, answer_id):
    # Fetch the answer to be edited.
    answer_to_edit = Answer.objects.get(id=answer_id)
    previous_answer = answer_to_edit.answer

    # Fetch the current problem ID
    # to be passed to the redirect.
    answer_problem = answer_to_edit.question
    problem_id = answer_problem.id

    # Fetch the assessment to be edited
    current_assessment = answer_problem.assessment

    # Initialize form.
    edit_answer_form = CreateAnswerForm(
        initial={
            'answer': answer_to_edit.answer
        }
    )

    # Successfully edit the answer.
    if request.method == 'POST' and 'edit-answer' in request.POST:
        edit_answer_form = CreateAnswerForm(request.POST)
        if edit_answer_form.is_valid():
            print('CODE IS REACHING THIS POINT')

            answer = edit_answer_form.cleaned_data['answer']
            answer_to_edit.answer = answer
            answer_to_edit.save()
            messages.success(request, f'Answer successfully changed from "{previous_answer}" to "{answer}".')
            return redirect(edit_problem, problem_id=problem_id)

    template_name = 'edit_assessment.html'

    context = {
        'edit_answer_form': edit_answer_form,
        'answer_to_edit': answer_to_edit,
        'current_assessment': current_assessment,
        'answer_problem': answer_problem,
    }
    return render(request, template_name, context)


def delete_answer(request, answer_id):
    # Fetch the answer to delete.
    answer_to_delete = Answer.objects.get(id=answer_id)

    # Delete the answer.
    answer_to_delete.delete()

    # Fetch the problem ID
    # to pass to the redirect function.
    problem_id = answer_to_delete.question.id

    return redirect(edit_problem, problem_id=problem_id)


def add_answer(request, problem_id):
    # Fetch the problem being edited.
    problem_to_edit = Problem.objects.get(id=problem_id)

    # Fetch the current user.
    current_user = problem_to_edit.creator

    # Initialize form.
    create_answer_form = CreateAnswerForm()

    # Fetch the user assessment
    user_assessments = Assessment.objects.filter(creator=current_user).exclude(title='')

    if request.method == 'POST' and 'create-answer' in request.POST:
        create_answer_form = CreateAnswerForm(request.POST)
        if create_answer_form.is_valid():
            answer = create_answer_form.cleaned_data['answer']
            new_answer = Answer.objects.create(
                creator=current_user,
                question=problem_to_edit,
                answer=answer,
            )
            new_answer.save()
            messages.success(request, f'Answer "{new_answer}" successfully added to problem "{problem_to_edit}".')
            return redirect(edit_problem, problem_id=problem_id)

    template_name = 'edit_assessment.html'

    context = {
        'create_answer_form': create_answer_form,
        'problem_to_edit': problem_to_edit,
        'problem_id': problem_id,
        'user_assessments': user_assessments,
    }
    return render(request, template_name, context)


def delete_problem(request, problem_id):
    # Fetch the problem to delete.
    problem_to_delete = Problem.objects.get(id=problem_id)

    # Delete the problem.
    problem_to_delete.delete()

    # Fetch the assessment ID
    # to pass to the redirect function.
    assessment_id = problem_to_delete.assessment.id

    return redirect(edit, assessment_id=assessment_id)


def add_problem(request, assessment_id):
    # Fetch the assessment being edited.
    assessment_to_edit = Assessment.objects.get(id=assessment_id)

    # Fetch the current user.
    current_user = assessment_to_edit.creator

    # Fetch problems related to the assessment to be edited.
    assessment_problems = Problem.objects.filter(creator=current_user, assessment=assessment_to_edit)

    # Initialize form.
    create_problem_form = CreateProblemForm()
    create_answer_form = CreateAnswerForm()

    # Fetch temporary assessment problems.
    assessment_problems = Problem.objects.filter(creator=current_user, assessment=assessment_to_edit)

    # Check if a problem is finished.
    problem_to_be_answered = assessment_problems.exclude(is_finished=True).last()

    if assessment_problems and not problem_to_be_answered:
        problem_to_be_answered = None
    elif assessment_problems and problem_to_be_answered:
        problem_to_be_answered = assessment_problems.last()
    print(problem_to_be_answered)

    # Successfully add problem.
    if request.method == 'POST' and 'create-problem' in request.POST:
        create_problem_form = CreateProblemForm(request.POST)
        if create_problem_form.is_valid():
            description = create_problem_form.cleaned_data['description']
            question = create_problem_form.cleaned_data['question']
            new_problem = Problem.objects.create(
                creator=current_user,
                assessment=assessment_to_edit,
                description=description,
                question=question,
                is_finished=False
            )
            new_problem.save()
            messages.success(request, f'Problem "{new_problem}" successfully added to problem "{assessment_to_edit}".')
            return redirect(add_problem, assessment_id=assessment_to_edit.id)

    # Fetch the answers related to the current problem.
    problems_and_answers = {}
    for problem in assessment_problems:
        problem_answers_list = []
        problem_answers_queryset = Answer.objects.filter(creator=current_user, question=problem)
        for problem_answer_object in problem_answers_queryset:
            problem_answers_list.append(problem_answer_object.answer)
        problems_and_answers.update({problem: problem_answers_list})

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
            return redirect(add_problem, assessment_id=assessment_to_edit.id)

    # All answers to a problem
    # have been created. Finish the problem.
    if request.method == 'POST' and 'problem-finished' in request.POST:
        create_answer_form = CreateAnswerForm(request.POST)
        if create_answer_form.is_valid():
            answer = create_answer_form.cleaned_data['answer']
            new_answer = Answer.objects.create(
                creator=current_user,
                question=problem_to_be_answered,
                answer=answer,
            )
            new_answer.save()
            return redirect(add_problem, assessment_id=assessment_to_edit.id)

    # Fetch the user assessments.
    user_assessments = Assessment.objects.filter(creator__id=current_user.id).exclude(title='')

    template_name = 'edit_assessment.html'

    context = {
        'create_problem_form': create_problem_form,
        'create_answer_form': create_answer_form,
        'assessment_to_edit': assessment_to_edit,
        'problem_id': assessment_id,
        'user_assessments': user_assessments,
        'assessment_problems': assessment_problems,
        'problem_to_be_answered': problem_to_be_answered,
    }
    return render(request, template_name, context)


def set_correct_answer(request, answer_id, from_view):
    correct_answer = Answer.objects.get(id=answer_id)
    correct_answer.is_correct_answer = True
    correct_answer.save()

    # Fetch the problem being edited to redirect to.
    problem_being_edited = correct_answer.question
    problem_id = problem_being_edited.id

    # Fetch the other answers to this problem
    # and, if any is set as correct, change value to False.
    other_answers = Answer.objects.filter(question=problem_being_edited, is_correct_answer=True).exclude(
        id=correct_answer.id)
    for answer in other_answers:
        answer.is_correct_answer = False
        answer.save()

    if from_view == 'create-assessment':
        return redirect(create_assessment)
    elif from_view == 'edit-problem':
        return redirect(edit_problem, problem_id=problem_id)


def finish_problem(request, problem_id, from_view):
    problem_being_edited = Problem.objects.get(id=problem_id)
    problem_being_edited.is_finished = True
    problem_being_edited.save()

    if from_view == 'create-assessment':
        return redirect(create_assessment)
    elif from_view == 'edit-problem':
        return redirect(edit_problem, problem_id=problem_id)


def find_assessment(request):
    # Initialize find assessment form.
    find_assessment_form = FindAssessmentForm()

    searched_assessment = None
    search = None

    if request.method == 'POST':
        find_assessment_form = FindAssessmentForm(request.POST)
        if find_assessment_form.is_valid():
            search = find_assessment_form.cleaned_data['search']
            searched_assessment_queryset = Assessment.objects.filter(id=search)
            if searched_assessment_queryset:
                searched_assessment = searched_assessment_queryset.first().title

    # Fetch first assessment problem to start assessment.
    first_problem = None
    if searched_assessment:
        first_problem = Problem.objects.filter(assessment=search).first()

    # Fetch the user.
    student = request.user

    assessments_already_answered = Result.objects.filter(student=student, assessment=search)

    # Check if there are multiple results for
    # this assessment and retain only the first one.
    # P.S. any other instance should be treated as 'created by mistake'.
    if len(assessments_already_answered) > 1:
        first = Result.objects.filter(student=student, assessment=search).first()
        Result.objects.filter(student=student, assessment=search).exclude(pk=first.pk).delete()
        assessment_already_answered = Result.objects.get(student=student, assessment=search)
    elif assessments_already_answered:
        assessment_already_answered = Result.objects.get(student=student, assessment=search)
    else:
        assessment_already_answered = None

    template_name = 'find_assessment.html'

    context = {
        'find_assessment_form': find_assessment_form,
        'searched_assessment': searched_assessment,
        'search': search,
        'first_problem': first_problem,
        'assessment_already_answered': assessment_already_answered,
    }
    return render(request, template_name, context)


def start_assessment(request, assessment_id, question_id, ):
    # Fetch the assessment to be carried out.
    assessment = Assessment.objects.get(id=assessment_id)

    # Fetch the problems related to this assessment.
    problems = Problem.objects.filter(assessment=assessment)

    # Fetch the current problem.
    current_problem = Problem.objects.get(id=question_id)

    # Fetch current problem available answers
    # and the correct answer.
    answers_list = []
    answers = Answer.objects.filter(question=current_problem)

    correct_answer = Answer.objects.get(question=current_problem, is_correct_answer=True).answer
    answer_given = AnswerGiven.objects.filter(student=request.user, question=current_problem)

    student_answer = None
    if not answer_given:
        print('code is here')
        answer_given = AnswerGiven(
            assessment=assessment,
            student=request.user,
            question=current_problem,
            correct_answer=correct_answer,
            student_answer=None
        )
        answer_given.save()
        print(answer_given)

    if answer_given:
        answer_given = AnswerGiven.objects.get(student=request.user, question=current_problem)
        student_answer = answer_given.student_answer
        answer_given.save()

    # Initiate assessment form.
    for answer in answers:
        answers_list.append((answer.answer, answer.answer))

    assessment_form = CarryOutAssessmentForm(choices=answers_list,
                                             initial={
                                                 'description': current_problem.description,
                                                 'question': current_problem.question,
                                                 'answer': student_answer}
                                             )

    # Fetch next problem to be answered.
    problems_list = list(problems)
    next_problem_in_list = None
    for problem_index in range(len(problems_list)):
        current_problem_index = problems_list.index(current_problem)
        for problem_in_list in problems_list:
            if current_problem_index == len(problems_list) - 1:
                next_problem_in_list = problems_list[0]
            else:
                next_problem_in_list = problems_list[current_problem_index + 1]
    next_problem = Problem.objects.get(question=next_problem_in_list)

    # POST request.
    if request.method == 'POST':
        student_answer = request.POST['answer']
        answer_given.student_answer = student_answer
        answer_given.save()
        # Initiate assessment form with current selected answer.
        assessment_form = CarryOutAssessmentForm(choices=answers_list,
                                                 initial={
                                                     'description': current_problem.description,
                                                     'question': current_problem.question,
                                                     'answer': student_answer}
                                                 )

    template_name = 'start_assessment.html'

    context = {
        'assessment': assessment,
        'problems': problems,
        'answers': answers,
        'assessment_form': assessment_form,
        'assessment_id': assessment_id,
        'next_problem': next_problem,
        'current_problem': current_problem,
    }
    return render(request, template_name, context)


def finish_assessment(request, assessment_id):
    # Fetch submitted assessment.
    assessment = Assessment.objects.get(id=assessment_id)

    # Fetch student.
    student = request.user

    # Fetch the answers given.
    answers_given = AnswerGiven.objects.filter(
        assessment=assessment,
        student=student,
    )

    # Context.
    correct_answers_number = 0
    for answer_given in answers_given:
        if answer_given.student_answer == answer_given.correct_answer:
            correct_answers_number += 1
    total_assessment_questions = len(answers_given)
    errors_number = 0
    for answer_given in answers_given:
        if answer_given.student_answer != answer_given.correct_answer:
            errors_number += 1
    correct_answers_percentage = (correct_answers_number * 100) / total_assessment_questions

    # Create a record for the result.
    Result.objects.create(
        student=student,
        assessment=assessment,
        correct_answers_number=correct_answers_number,
        total_assessment_questions=total_assessment_questions,
        errors_number=errors_number,
        correct_answers_percentage=correct_answers_percentage,
    )

    assessments_already_answered = Result.objects.filter(student=student, assessment=assessment)
    if len(assessments_already_answered) == 1:
        assessment_already_answered = Result.objects.get(student=student, assessment=assessment)
        assessment_already_answered.save()
    else:
        first = Result.objects.filter(student=student, assessment=assessment).first()
        Result.objects.filter(student=student, assessment=assessment).exclude(pk=first.pk).delete()
        assessment_already_answered = Result.objects.get(student=student, assessment=assessment)
        assessment_already_answered.save()
        print(assessment_already_answered)
        return redirect(find_assessment)

    template_name = 'finish_assessment.html'

    context = {
        'assessment': assessment,
        'correct_answers_number': correct_answers_number,
        'total_assessment_questions': total_assessment_questions,
        'errors_number': errors_number,
        'correct_answers_percentage': correct_answers_percentage,
        'assessment_already_answered': assessment_already_answered,
    }
    return render(request, template_name, context)


def check_results(request):
    # Initialize check results form.
    check_results_form = CheckResultsForm()

    # Display all student results.
    if request.method == 'POST':
        check_results_form = CheckResultsForm(request.POST)
        if check_results_form.is_valid():
            student_id = check_results_form.cleaned_data['student_id']
            print(student_id)
            student = User.objects.get(id=student_id, role='Student')
            print(student)
            student_results = Result.objects.filter(student=student)

    template_name = 'check_results.html'

    context = {
        'check_results_form': check_results_form,
        'student_results': student_results,
        'student': student,
    }
    return render(request, template_name, context)
