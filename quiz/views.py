from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.views.generic import DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Teacher, Student, Quiz, QuizAttempt, QuestionResponse, Answer
from .forms import (
     
    QuizForm, QuestionForm, MultipleChoiceAnswerFormSet,
    TrueFalseAnswerFormSet, ShortAnswerForm
)
import json


# Teacher Views
@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher:
        return redirect('login')
    
    teacher = Teacher.objects.get(user=request.user)
    active_quizzes = Quiz.objects.filter(teacher=teacher, status='active')
    draft_quizzes = Quiz.objects.filter(teacher=teacher, status='draft')
    completed_quizzes = Quiz.objects.filter(teacher=teacher, status='completed')
    
    # Get some statistics
    total_quizzes = Quiz.objects.filter(teacher=teacher).count()
    total_students = Student.objects.filter(quiz_attempts__quiz__teacher=teacher).distinct().count()
    avg_score = QuizAttempt.objects.filter(
        quiz__teacher=teacher, 
        completed=True
    ).aggregate(avg_score=Avg('score'))['avg_score'] or 0
    
    context = {
        'active_quizzes': active_quizzes,
        'draft_quizzes': draft_quizzes,
        'completed_quizzes': completed_quizzes,
        'total_quizzes': total_quizzes,
        'total_students': total_students,
        'avg_score': round(avg_score, 1)
    }
    
    return render(request, 'quiz/teacher/dashboard.html', context)


class QuizCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'quiz/teacher/quiz_form.html'
    success_url = reverse_lazy('teacher_dashboard')
    
    def test_func(self):
        return self.request.user.is_teacher
    
    def form_valid(self, form):
        form.instance.teacher = Teacher.objects.get(user=self.request.user)
        return super().form_valid(form)



class QuizUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'quiz/teacher/quiz_form.html'
    
    def test_func(self):
        quiz = self.get_object()
        return self.request.user.is_teacher and quiz.teacher.user == self.request.user
    
    def get_success_url(self):
        return reverse_lazy('quiz_detail', kwargs={'pk': self.object.pk})



class QuizDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Quiz
    template_name = 'quiz/teacher/quiz_details.html'
    context_object_name = 'quiz'
    
    def test_func(self):
        quiz = self.get_object()
        return self.request.user.is_teacher and quiz.teacher.user == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.get_object()
        
        # Get quiz statistics
        attempts = QuizAttempt.objects.filter(quiz=quiz, completed=True)
        context['total_attempts'] = attempts.count()
        context['avg_score'] = attempts.aggregate(avg=Avg('score'))['avg'] or 0
        context['pass_rate'] = attempts.filter(score__gte=quiz.passing_score).count() / max(attempts.count(), 1) * 100
        
        # Get recent results
        context['recent_results'] = attempts.order_by('-end_time')[:5]
        
        # Get question statistics
        questions = quiz.get_questions()
        question_stats = []
        
        for question in questions:
            correct_count = QuestionResponse.objects.filter(
                question=question, 
                is_correct=True, 
                attempt__completed=True
            ).count()
            
            total_count = QuestionResponse.objects.filter(
                question=question,
                attempt__completed=True
            ).count()
            
            correct_percentage = (correct_count / max(total_count, 1)) * 100
            avg_time = QuestionResponse.objects.filter(
                question=question,
                attempt__completed=True
            ).aggregate(avg_time=Avg('time_spent'))['avg_time'] or 0
            
            question_stats.append({
                'question': question,
                'correct_percentage': correct_percentage,
                'avg_time': avg_time
            })
        
        context['question_stats'] = question_stats
        
        return context


@login_required
def add_question(request, quiz_id):
    if not request.user.is_teacher:
        return redirect('account:login')
    
    quiz = get_object_or_404(Quiz, pk=quiz_id, teacher__user=request.user)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        
        if form.is_valid():
            question_type = form.cleaned_data.get('question_type')
            question = form.save(commit=False)
            question.quiz = quiz
            question.order = quiz.get_question_count() + 1
            question.save()
            
            if question_type == 'multiple-choice':
                formset = MultipleChoiceAnswerFormSet(request.POST, instance=question)
                if formset.is_valid():
                    formset.save()
            elif question_type == 'true-false':
                formset = TrueFalseAnswerFormSet(request.POST, instance=question)
                if formset.is_valid():
                    formset.save()
            elif question_type == 'short-answer':
                answer_form = ShortAnswerForm(request.POST)
                if answer_form.is_valid():
                    answer = Answer(
                        question=question,
                        text=answer_form.cleaned_data.get('correct_answer'),
                        is_correct=True
                    )
                    answer.save()
            
            return redirect('quiz_detail', pk=quiz.pk)
    else:
        form = QuestionForm()
    
    return render(request, 'quiz/teacher/add_question.html', {
        'form': form,
        'quiz': quiz
    })