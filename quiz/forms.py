from django import forms
from django.forms import inlineformset_factory
from quiz.models import Quiz, Question, Answer


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
            'explanation': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional that might not be used for all question types
        self.fields['image'].required = False
        self.fields['explanation'].required = False
        
    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get('question_type')
        
        # Short answer questions are handled through the Answer model now
        return cleaned_data

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

class QuizAccessForm(forms.Form):
    quiz_id = forms.UUIDField(label="Quiz ID")
    student_id = forms.CharField(max_length=20, label="Student ID")






class AnswerInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        # For multiple choice questions, ensure at least one choice is marked as correct
        if self.instance.question_type == 'multiple-choice':
            has_correct = False
            for form in self.forms:
                if form.cleaned_data.get('is_correct'):
                    has_correct = True
                    break
            if not has_correct:
                raise forms.ValidationError("At least one choice must be marked as correct.")

# This would typically be used in the admin or in a custom view
AnswerFormSet = forms.inlineformset_factory(
    Question, 
    Answer, 
    fields=('text', 'is_correct'),
    extra=4,
    formset=AnswerInlineFormSet,
    can_delete=True
)
