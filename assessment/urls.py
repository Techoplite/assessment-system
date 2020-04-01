from django.urls import path
from . import views

urlpatterns = [
    path('create-assessment/', views.create_assessment, name='create-assessment'),
    path('delete-assessment/', views.delete_assessment, name='delete-assessment'),
    path('delete-assessment/delete/<int:assessment_id>/', views.delete, name='delete'),
    path('edit-assessment/edit/', views.edit_assessment, name='edit-assessment'),
    path('edit-assessment/edit/<int:assessment_id>/', views.edit, name='edit'),
]
