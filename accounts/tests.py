from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from .admin import UserCreationForm
from .models import User


class UserCreationFormTest(TestCase):

    def test_valid_form_teacher(self):
        data = {
            'email': 'jack.sparrow@example.com',
            'first_name': 'Jack',
            'last_name': 'Sparrow',
            'role': 'Teacher',
            'password1': 'jackpass1',
            'password2': 'jackpass1',
        }
        form = UserCreationForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.data['role'] == 'Teacher')
        self.assertFalse(form.data['role'] == 'Student')

    def test_valid_form_student(self):
        data = {
            'email': 'jack.sparrow@example.com',
            'first_name': 'Jack',
            'last_name': 'Sparrow',
            'role': 'Student',
            'password1': 'jackpass1',
            'password2': 'jackpass1',
        }
        form = UserCreationForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.data['role'] == 'Student')
        self.assertFalse(form.data['role'] == 'Teacher')

    def test_invalid_email(self):
        data = {
            'email': 'jack.sparrowexample.com',
            'first_name': 'Jack',
            'last_name': 'Sparrow',
            'role': 'Teacher',
            'password1': 'jackpass1',
            'password2': 'jackpass1',
        }
        form = UserCreationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_password(self):
        data = {
            'email': 'jack.sparrow@example.com',
            'first_name': 'Jack',
            'last_name': 'Sparrow',
            'role': 'Teacher',
            'password1': 'jackpass1',
            'password2': 'jackpass2',
        }
        form = UserCreationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_role(self):
        data = {
            'email': 'jack.sparrow@example.com',
            'first_name': 'Jack',
            'last_name': 'Sparrow',
            'role': 'Tutor',
            'password1': 'jackpass1',
            'password2': 'jackpass1',
        }
        form = UserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.data['role'] == 'Tutor')

    def test_invalid_name(self):
        data = {
            'email': 'jack.sparrow@example.com',
            'first_name': 'test for a name longer than fifty characters, which should not work',
            'last_name': '',
            'role': 'Student',
            'password1': 'jackpass1',
            'password2': 'jackpass1',
        }
        form = UserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.data['first_name']) > 50)

    def test_save(self):
        data = {
            'email': 'jack.sparrow@example.com',
            'first_name': 'Jack',
            'last_name': 'Sparrow',
            'role': 'Teacher',
            'password1': 'jackpass1',
            'password2': 'jackpass1',
        }
        form = UserCreationForm(data=data)
        form.save()
        self.assertTrue(form.is_valid())
        self.assertTrue(form.data['role'] == 'Teacher')
        self.assertFalse(form.data['role'] == 'Student')


# class SignUpViewTest(TestCase):
#
#     def test_get_request(self):
#         path = '/signup/'
#         data = {
#             'email': '',
#             'first_name': '',
#             'last_name': '',
#             'role': 'Student',
#             'password1': '',
#             'password2': '',
#         }
#         form = UserCreationForm()
#         response = self.client.get(path, data=None)
#         self.assertEqual(response.status_code, 200)
#         print("Form: {}".format(form.__dict__))
#         print("Response form: {}".format(response.context['form'].__dict__))
#         self.assertEqual(response.context['form'], form)


