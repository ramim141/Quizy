from django.urls import path
from . import views

urlpatterns = [
   
   
   # Teacher URLs
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/quiz/create/', views.QuizCreateView.as_view(), name='quiz_create'),
    path('teacher/quiz/<uuid:quiz_id>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('teacher/quiz/<uuid:quiz_id>/edit/', views.QuizUpdateView.as_view(), name='quiz_edit'),
    path('teacher/quiz/<uuid:quiz_id>/add-question/', views.add_question, name='add_question'),
    path('teacher/leaderboard/', views.teacher_leaderboard, name='teacher_leaderboard'),
    path('teacher/questions/<int:question_id>/preview/', views.preview_question, name='preview_question'),
    
    path('teacher/quizzes/<uuid:pk>/preview/', views.preview_quiz, name='preview_quiz'),
    
    
    
     # Student URLs
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/quiz/<int:attempt_id>/', views.take_quiz, name='take_quiz'),
    path('student/results/<int:attempt_id>/', views.quiz_results, name='quiz_results'),
    
     # Quiz Access URLs
    path('access/', views.quiz_access, name='quiz_access'),
    path('access/<uuid:quiz_id>/', views.quiz_access, name='quiz_access_with_id'),
    
     # Quiz Deletion URL
    path('quizzes/<uuid:quiz_id>/delete/', views.QuizDeleteView.as_view(), name='quiz_delete'),
    path('quiz/<uuid:quiz_id>/mark-completed/', views.mark_quiz_completed, name='mark_quiz_completed'),
    path('quiz/<uuid:quiz_id>/mark-active/' , views.mark_quiz_active, name='mark_quiz_active'),
    
    path('teacher/quizzes/<uuid:quiz_id>/questions/<int:question_id>/edit/', 
         views.edit_question, name='edit_question'),
    path('teacher/quizzes/<uuid:quiz_id>/questions/<int:question_id>/delete/', 
         views.delete_question, name='delete_question'),
    
]
