from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .admin import UserCreationForm
from .forms import LoginForm
from core.views import home


def signup(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            try:
                validate_password(password1, user)
                user = form.save(commit=True)
                authenticate(request, email=email, password=password1)
                login(request, user)
                messages.success(request,
                                 f'Good news {form.cleaned_data["first_name"]}, you have successfully signed up.')
            except ValidationError as e:
                form.add_error('password1', e)
                messages.error(request, 'This password is too common. Choose a better one.')
                return redirect(signup)

            return redirect(home)
    template_name = 'signup.html'
    context = {
        'form': form,
    }
    return render(request, template_name, context)


def login_view(request):
    form = LoginForm()
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Hi {user.first_name}, you have successfully logged in.')
            return redirect(home)
    template_name = 'login.html'
    context = {'form': form}
    return render(request, template_name, context)


def logout_view(request):
    logout(request)
    return redirect(home)
