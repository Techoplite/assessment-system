from django.test import TestCase, Client
from .admin import UserCreationForm
from .models import User


class SignUpViewTest(TestCase):

    def test_valid_form_teacher(self):
        data = {
            'email': 'jack.sparrow@example.com',
            'first_name': 'Jack',
            'last_name': 'Sparrow',
            'role': 'Teacher',
            'password1': 'jackpass1',
            'password2': 'jackpass1'
        }
        form = UserCreationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_valid_form_student(self):
        data = {
            'email': 'jack.sparrow@example.com',
            'first_name': 'Jack',
            'last_name': 'Sparrow',
            'role': 'Student',
            'password1': 'jackpass1',
            'password2': 'jackpass1'
        }
        form = UserCreationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        data = {
            'email': 'jack.sparrowexample.com',
            'first_name': 'Jack',
            'last_name': 'Sparrow',
            'role': 'Teacher',
            'password1': 'jackpass1',
            'password2': 'jackpass1'
        }
        form = UserCreationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_role(self):
        data = {
            'email': 'jack.sparrow@example.com',
            'first_name': '',
            'last_name': 'Sparrow',
            'role': 'Tutor',
            'password1': 'jackpass1',
            'password2': 'jackpass1'
        }
        form = UserCreationForm(data=data)
        self.assertFalse(form.is_valid())
