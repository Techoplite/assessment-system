from django.urls import path
from . import views

urlpatterns = [
    path('create-assessment/', views.create_assessment, name='create-assessment'),
]
