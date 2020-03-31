from django.test import TestCase
from assessment.forms import CreateProblemForm, CreateAssessmentForm
from assessment.models import Problem
from accounts.models import User


class TeacherHomeViewTest(TestCase):
    def setUp(self):
        user = User.objects.create(
            email='john.smith@example.com',
            first_name='John',
            last_name='Smith',
            password='johnpass1'
        )

        user.role = 'Teacher'
        user.save()

        self.client.login(email='john.smith@example.com', password='johnpass1')
        print(User.objects.all())

    def test_successfully_create_problem_with_no_description(self):
        """
        When a question is provided a problem
        is successfully created.
        :return: HttpResponse
        """
        user = User.objects.get(id=1)
        self.client.login(email=user.email, password=user)

        data = {
            'description': '',
            'question': 'What is the capital of England?'
        }

        # Initialize forms.
        CreateProblemForm(data)
        CreateAssessmentForm()

        response = self.client.post('/create-assessment/', data)

        qs = Problem.objects.all()
        values = '<QuerySet [<Problem: What is the capital of England?>]>'

        self.assertQuerysetEqual(qs, values)
        self.assertEqual(response.status_code, 200)
