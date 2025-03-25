from django.urls import path
from . import views

urlpatterns = [
   
   
   # Teacher URLs
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/quiz/create/', views.QuizCreateView.as_view(), name='quiz_create'),
    path('teacher/quiz/<uuid:pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('teacher/quiz/<uuid:pk>/edit/', views.QuizUpdateView.as_view(), name='quiz_edit'),
    path('teacher/quiz/<uuid:quiz_id>/add-question/', views.add_question, name='add_question'),
    
]
