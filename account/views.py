from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import json
from account.forms import StudentSignUpForm, TeacherSignUpForm, LoginForm


# register

# def register(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         confirm_password = request.POST.get('confirm_password')

#         if password == confirm_password:
#             if User.objects.filter(username=username).exists():
#                 messages.error(request, 'Username already exists')
#             elif User.objects.filter(email=email).exists():
#                 messages.error(request, 'Email already exists')
#             else:
#                 User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
#                 messages.success(request, 'Registration successful. Please log in.')
#                 # return redirect('account:login')
#                 return render(request, 'account/register_success.html')
#         else:
#             messages.error(request, 'Passwords do not match')
#     return render(request, 'account/register.html')


def register_view(request):
    """Combined registration page with tabs for teacher and student registration"""
    if request.method == 'POST':
        if 'teacher_signup' in request.POST:
            form = TeacherSignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(
                    request, 'Teacher account created successfully! Welcome to QuizMaster.')
               # return redirect('account:login')
                return render(request, 'account/register_success.html')
            else:
                student_form = StudentSignUpForm()
                return render(request, 'account/register.html', {
                    'teacher_form': form,
                    'student_form': student_form
                })
        elif 'student_signup' in request.POST:
            form = StudentSignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(
                    request, 'Student account created successfully! Welcome to QuizMaster.')
                return render(request, 'account/register_success.html')
                
            else:
                teacher_form = TeacherSignUpForm()
                return render(request, 'account/register.html', {
                    'teacher_form': teacher_form,
                    'student_form': form
                })
    else:
        teacher_form = TeacherSignUpForm()
        student_form = StudentSignUpForm()

    return render(request, 'account/register.html', {
        'teacher_form': teacher_form,
        'student_form': student_form
    })


def teacher_signup(request):
  if request.method == 'POST':
      form = TeacherSignUpForm(request.POST)
      if form.is_valid():
          user = form.save()
          login(request, user)
          messages.success(request, 'Account created successfully! Welcome to QuizMaster.')
          return redirect('teacher_dashboard') # teacher dashboard
  else:
      form = TeacherSignUpForm()
  
  return render(request, 'teacher_signup.html', {'form': form})

def student_signup(request):
  if request.method == 'POST':
      form = StudentSignUpForm(request.POST)
      if form.is_valid():
          user = form.save()
          login(request, user)
          messages.success(request, 'Account created successfully! Welcome to QuizMaster.')
          return redirect('student_dashboard')
  else:
      form = StudentSignUpForm()
  
  return render(request, 'student_signup.html', {'form': form})



def login_view(request):
  if request.method == 'POST':
      form = LoginForm(request.POST)
      if form.is_valid():
          username = form.cleaned_data.get('username')
          password = form.cleaned_data.get('password')
          user = authenticate(username=username, password=password)
          if user is not None:
              login(request, user)
              if user.is_teacher:
                  return redirect('teacher_dashboard')
              else:
                  return redirect('student_dashboard')
          else:
              messages.error(request, 'Invalid username or password')
  else:
      form = LoginForm()
  
  return render(request, 'account/login.html', {'form': form})

# def user_login(request):  # Renamed from login to user_login
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             auth_login(request, user)  # Use Django's built-in login function
#             return redirect('home')  # Redirect to the home page
#         else:
#             messages.error(request, 'Invalid username or password')
#     return render(request, 'account/login.html')


# def user_logout(request):
#     logout(request)
#     return redirect('home')  # Redirect to the home page
def logout_view(request):
    logout(request)
    return redirect('account:login')



