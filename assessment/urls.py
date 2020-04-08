from django.urls import path
from . import views

urlpatterns = [
    path('create-assessment/', views.create_assessment, name='create-assessment'),
    path('delete-assessment/', views.delete_assessment, name='delete-assessment'),
    path('delete-assessment/delete/<int:assessment_id>/', views.delete, name='delete'),
    path('edit-assessment/edit/', views.edit_assessment, name='edit-assessment'),
    path('edit-assessment/edit/<int:assessment_id>/', views.edit, name='edit'),
    path('edit-problem/<int:problem_id>/', views.edit_problem, name='edit-problem'),
    path('edit-answer/<int:answer_id>/', views.edit_answer, name='edit-answer'),
    path('delete-answer/<int:answer_id>/', views.delete_answer, name='delete-answer'),
    path('set-correct-answer/<int:answer_id>/<str:from_view>/', views.set_correct_answer, name='set-correct-answer'),
    path('delete-problem/<int:problem_id>/', views.delete_problem, name='delete-problem'),
    path('add-answer/<int:problem_id>/', views.add_answer, name='add-answer'),
    path('add-problem/<int:assessment_id>/', views.add_problem, name='add-problem'),
    path('create-assessment/finish-problem/<int:problem_id>/<str:from_view>/', views.finish_problem, name='finish-problem'),
]
