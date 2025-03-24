from django.urls import path
from . import views

urlpatterns = [
    # path('login/', user_login, name='login'),
    # path('logout/', user_logout, name='logout'),
    # path('register/', register, name='register'),
    
     # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('signup/teacher/', views.teacher_signup, name='teacher_signup'),
    path('signup/student/', views.student_signup, name='student_signup'),
    
]
