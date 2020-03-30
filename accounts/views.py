from django.shortcuts import render

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
            form.save()
            messages.success(request, f'Good news {form.cleaned_data["first_name"]}, you have successfully signed up.')
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