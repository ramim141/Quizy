from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms import inlineformset_factory
from .models import User, Teacher, Student, Quiz, Question, Answer


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = [
            'title', 'description', 'time_limit', 'passing_score', 
            'max_attempts', 'shuffle_questions', 'prevent_tab_switch',
            'show_results_immediately', 'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'points', 'image', 'explanation']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'explanation': forms.Textarea(attrs={'rows': 2}),
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']

# For multiple choice questions
MultipleChoiceAnswerFormSet = inlineformset_factory(
    Question, 
    Answer, 
    form=AnswerForm, 
    extra=4, 
    min_num=2, 
    validate_min=True
)

# For true/false questions
TrueFalseAnswerFormSet = inlineformset_factory(
    Question, 
    Answer, 
    form=AnswerForm, 
    extra=2, 
    max_num=2, 
    validate_max=True
)

class ShortAnswerForm(forms.Form):
    correct_answer = forms.CharField(max_length=255)