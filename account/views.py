from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.models import User

# register

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
            else:
                User.objects.create_user(username=username, email=email, password=password)
                messages.success(request, 'Registration successful. Please log in.')
                return redirect('account:login')  # Redirect to the user_login view
        else:
            messages.error(request, 'Passwords do not match')
    return render(request, 'account/register.html')

def user_login(request):  # Renamed from login to user_login
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # Use Django's built-in login function
            return redirect('home')  # Redirect to the home page
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'account/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')  # Redirect to the home page
