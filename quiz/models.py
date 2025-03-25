from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
from account.models import Teacher, Student
from django.urls import reverse


class Quiz(models.Model):
    QUIZ_STATUS = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='quizzes')
    time_limit = models.IntegerField(
        help_text="Time limit in minutes", default=30)
    passing_score = models.IntegerField(
        default=60, help_text="Passing score in percentage")
    max_attempts = models.IntegerField(default=1)
    shuffle_questions = models.BooleanField(default=False)
    prevent_tab_switch = models.BooleanField(default=True)
    show_results_immediately = models.BooleanField(default=True)
    status = models.CharField(
        max_length=10, choices=QUIZ_STATUS, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tittle

    def get_absolute_url(self):
        return reverse('quiz_detail', kwargs={'pk': self.pk})

    def get_questions(self):
        return self.questions.all() 

    def get_question_count(self):
        return self.questions.count() 


class Question(models.Model):
    QUESTION_TYPES = (
        ('multiple-choice', 'Multiple Choice'),
        ('true-false', 'True/False'),
        ('short-answer', 'Short Answer'),
    )

    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    points = models.IntegerField(default=1)
    image = models.ImageField(
        upload_to='question_images/', blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.quiz.title} - Question {self.order}"

    def get_answers(self):
        return self.answers.all() if self.question_type == 'multiple-choice' else None


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.text} - {self.text}"


class QuizAttempt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.student.user.username} - {self.quiz.title}"
    
    def calculate_score(self):
        total_questions = self.quiz.get_question_count()
        if total_questions == 0:
            return 0
        
        correct_answers = self.responses.filter(is_correct=True).count()
        return (correct_answers / total_questions) * 100
    
    def get_time_taken(self):
        if not self.end_time:
            return None
        
        time_taken = self.end_time - self.start_time
        minutes, seconds = divmod(time_taken.seconds, 60)
        return f"{minutes}:{seconds:02d}"
    
    def is_passed(self):
        return False if self.score is None else self.score >= self.quiz.passing_score

class QuestionResponse(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    text_response = models.TextField(blank=True, null=True)  # For short answer questions
    is_correct = models.BooleanField(default=False)
    time_spent = models.IntegerField(default=0, help_text="Time spent in seconds")
    
    def __str__(self):
        return f"{self.attempt.student.user.username} - {self.question.text}"