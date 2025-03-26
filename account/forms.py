from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms import inlineformset_factory
from .models import User, Teacher, Student

class TeacherSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_teacher = True
        user.save()
        Teacher.objects.create(user=user)
        return user
class StudentSignUpForm(UserCreationForm):
    student_id = forms.CharField(max_length=20, required=True)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'student_id')
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.save()
        Student.objects.create(
            user=user,
            student_id=self.cleaned_data.get('student_id')
        )
        return user
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    



   