from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, F
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Teacher, Student, Quiz, QuizAttempt, QuestionResponse, Answer, Question
from .forms import (
     
    QuizForm, QuestionForm, MultipleChoiceAnswerFormSet,
    TrueFalseAnswerFormSet, ShortAnswerForm, QuizAccessForm
)
import json
from django.contrib import messages
from django.utils import timezone
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
    
    





# Student Views
@login_required
def student_dashboard(request):
    if not request.user.is_student:
        return redirect('login')
    
    student = Student.objects.get(user=request.user)
    attempts = QuizAttempt.objects.filter(student=student)
    
    completed_attempts = attempts.filter(completed=True)
    ongoing_attempts = attempts.filter(completed=False)
    
    context = {
        'student': student,
        'completed_attempts': completed_attempts,
        'ongoing_attempts': ongoing_attempts
    }
    
    return render(request, 'quiz/student/dashboard.html', context)




@login_required
def take_quiz(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id)
    
    # Check if the student is authorized to take this quiz
    if request.user.is_student and attempt.student.user != request.user:
        messages.error(request, 'You are not authorized to take this quiz')
        return redirect('student_dashboard')
    
    # Check if the quiz is already completed
    if attempt.completed:
        return redirect('quiz_results', attempt_id=attempt.id)
    
    quiz = attempt.quiz
    questions = list(quiz.get_questions())
    
    if quiz.shuffle_questions:
        import random
        random.shuffle(questions)
    
    # Handle form submission
    if request.method == 'POST':
        # Process all question responses
        for question in questions:
            if question.question_type == 'multiple-choice' or question.question_type == 'true-false':
                answer_id = request.POST.get(f'question_{question.id}')
                if answer_id:
                    answer = Answer.objects.get(id=answer_id)
                    is_correct = answer.is_correct
                    
                    QuestionResponse.objects.create(
                        attempt=attempt,
                        question=question,
                        answer=answer,
                        is_correct=is_correct,
                        time_spent=int(request.POST.get(f'time_spent_{question.id}', 0))
                    )
            elif question.question_type == 'short-answer':
                text_response = request.POST.get(f'question_{question.id}')
                correct_answer = question.answers.filter(is_correct=True).first()
                
                # Simple exact match for short answer
                is_correct = False
                if correct_answer and text_response:
                    is_correct = text_response.lower().strip() == correct_answer.text.lower().strip()
                
                QuestionResponse.objects.create(
                    attempt=attempt,
                    question=question,
                    text_response=text_response,
                    is_correct=is_correct,
                    time_spent=int(request.POST.get(f'time_spent_{question.id}', 0))
                )
        
        # Mark the attempt as completed
        attempt.end_time = timezone.now()
        attempt.completed = True
        attempt.score = attempt.calculate_score()
        attempt.save()
        
        return redirect('quiz/student/quiz_results', attempt_id=attempt.id)
    
    context = {
        'attempt': attempt,
        'quiz': quiz,
        'questions': questions,
        'time_limit_seconds': quiz.time_limit * 60,
        'prevent_tab_switch': quiz.prevent_tab_switch
    }
    
    return render(request, 'quiz/student/take_quiz.html', context)



@login_required
def quiz_results(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id, completed=True)
    
    # Check if the user is authorized to view these results
    if request.user.is_student and attempt.student.user != request.user:
        messages.error(request, 'You are not authorized to view these results')
        return redirect('student_dashboard')
    
    if request.user.is_teacher and attempt.quiz.teacher.user != request.user:
        messages.error(request, 'You are not authorized to view these results')
        return redirect('teacher_dashboard')
    
    quiz = attempt.quiz
    responses = attempt.responses.all()
    
    # Calculate strengths and areas for improvement
    strengths = []
    improvements = []
    
    # Group questions by type and check performance
    question_types = {}
    for response in responses:
        q_type = response.question.question_type
        if q_type not in question_types:
            question_types[q_type] = {'correct': 0, 'total': 0}
        
        question_types[q_type]['total'] += 1
        if response.is_correct:
            question_types[q_type]['correct'] += 1
    
    # Determine strengths and weaknesses based on performance
    for q_type, stats in question_types.items():
        percentage = (stats['correct'] / stats['total']) * 100
        if percentage >= 80:
            if q_type == 'multiple-choice':
                strengths.append('Strong understanding of multiple choice questions')
            elif q_type == 'true-false':
                strengths.append('Excellent grasp of true/false concepts')
            elif q_type == 'short-answer':
                strengths.append('Good ability to provide short answers')
        elif percentage <= 50:
            if q_type == 'multiple-choice':
                improvements.append('Need to improve on multiple choice questions')
            elif q_type == 'true-false':
                improvements.append('Review true/false concepts')
            elif q_type == 'short-answer':
                improvements.append('Practice providing more accurate short answers')
    
    # Get class average for comparison
    class_avg = QuizAttempt.objects.filter(
        quiz=quiz,
        completed=True
    ).aggregate(avg=Avg('score'))['avg'] or 0
    
    # Calculate percentile
    better_than_count = QuizAttempt.objects.filter(
        quiz=quiz,
        completed=True,
        score__lt=attempt.score
    ).count()
    
    total_attempts = QuizAttempt.objects.filter(
        quiz=quiz,
        completed=True
    ).count()
    
    percentile = (better_than_count / max(total_attempts - 1, 1)) * 100
    
    context = {
        'attempt': attempt,
        'quiz': quiz,
        'responses': responses,
        'strengths': strengths,
        'improvements': improvements,
        'class_avg': class_avg,
        'percentile': percentile,
        'passed': attempt.is_passed()
    }
    
    return render(request, 'quiz/student/quiz_results.html', context)

def quiz_access(request, quiz_id=None):
  if request.method == 'POST':
      form = QuizAccessForm(request.POST)
      if form.is_valid():
          quiz_id = form.cleaned_data.get('quiz_id')
          student_id = form.cleaned_data.get('student_id')
          
          try:
              student = Student.objects.get(student_id=student_id)
              quiz = Quiz.objects.get(id=quiz_id)
              
              # Check if the quiz is active
              if quiz.status != 'active':
                  messages.error(request, f'This quiz is not currently active. Current status: {quiz.get_status_display()}')
                  return render(request, 'quiz/student/quiz_access.html', {'form': form})
              
              # Check if the student has reached the maximum number of attempts
              attempts_count = QuizAttempt.objects.filter(student=student, quiz=quiz).count()
              if attempts_count >= quiz.max_attempts:
                  messages.error(request, f'You have reached the maximum number of attempts ({quiz.max_attempts}) for this quiz.')
                  return render(request, 'quiz/student/quiz_access.html', {'form': form})
              
              # Check if the student has an incomplete attempt
              incomplete_attempt = QuizAttempt.objects.filter(student=student, quiz=quiz, completed=False).first()
              if incomplete_attempt:
                  messages.info(request, 'You have an incomplete attempt. Continuing from where you left off.')
                  return redirect('quiz/student/take_quiz', attempt_id=incomplete_attempt.id)
              
              # Create a new attempt
              attempt = QuizAttempt.objects.create(
                  student=student,
                  quiz=quiz
              )
              
              messages.success(request, f'Successfully accessed quiz: {quiz.title}')
              return redirect('quiz/student/take_quiz', attempt_id=attempt.id)
          except Student.DoesNotExist:
              messages.error(request, 'Invalid student ID. Please check your student ID and try again.')
          except Quiz.DoesNotExist:
              messages.error(request, 'Invalid quiz ID. Please check the quiz ID and try again.')
          except Exception as e:
              messages.error(request, f'An error occurred: {str(e)}')
  else:
      # If quiz_id is provided in the URL, pre-fill the form
      initial_data = {}
      if quiz_id:
          initial_data['quiz_id'] = quiz_id
          # Try to get quiz details to show in the template
          try:
              quiz = Quiz.objects.get(id=quiz_id)
              # Pass quiz to the template context
              return render(request, 'quiz/student/quiz_access.html', {
                  'form': QuizAccessForm(initial=initial_data),
                  'quiz': quiz
              })
          except Quiz.DoesNotExist:
              messages.error(request, 'The requested quiz does not exist.')
      
      form = QuizAccessForm(initial=initial_data)
  
  return render(request, 'quiz/student/quiz_access.html', {'form': form})


class QuizDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Quiz
    template_name = 'quiz/teacher/quiz_confirm_delete.html'
    success_url = reverse_lazy('teacher_dashboard')
    
    def test_func(self):
        quiz = self.get_object()
        return self.request.user.is_teacher and quiz.teacher.user == self.request.user
    
    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(request, f'Quiz "{quiz.title}" has been deleted successfully.')
        return super().delete(request, *args, **kwargs)
    
    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to delete this quiz.")
        return super().handle_no_permission()



# Add this new view function for the teacher leaderboard
@login_required
def teacher_leaderboard(request):
    if not request.user.is_teacher:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('account:login')
    
    teacher = Teacher.objects.get(user=request.user)
    
    # Get filter parameters
    quiz_filter = request.GET.get('quiz', None)
    time_period = request.GET.get('period', 'all')  # all, month, week
    
    # Base query - get all completed attempts for this teacher's quizzes
    attempts = QuizAttempt.objects.filter(
        quiz__teacher=teacher,
        completed=True
    )
    
    # Apply filters
    if quiz_filter:
        attempts = attempts.filter(quiz_id=quiz_filter)
    
    if time_period == 'month':
        one_month_ago = timezone.now() - timezone.timedelta(days=30)
        attempts = attempts.filter(end_time__gte=one_month_ago)
    elif time_period == 'week':
        one_week_ago = timezone.now() - timezone.timedelta(days=7)
        attempts = attempts.filter(end_time__gte=one_week_ago)
    
    # Get all quizzes for the filter dropdown
    quizzes = Quiz.objects.filter(teacher=teacher)
    
    # Get top students by average score
    student_stats = []
    
    # Get unique students who have taken this teacher's quizzes
    students = Student.objects.filter(quiz_attempts__in=attempts).distinct()
    
    for student in students:
        student_attempts = attempts.filter(student=student)
        avg_score = student_attempts.aggregate(avg=Avg('score'))['avg'] or 0
        total_attempts = student_attempts.count()
        total_passed = student_attempts.filter(score__gte=F('quiz__passing_score')).count()
        pass_rate = (total_passed / total_attempts * 100) if total_attempts > 0 else 0
        
        # Get the student's best quiz
        best_attempt = student_attempts.order_by('-score').first()
        best_quiz = best_attempt.quiz.title if best_attempt else "N/A"
        best_score = best_attempt.score if best_attempt else 0
        
        # Calculate average time per quiz
        total_time = timezone.timedelta(seconds=0)
        for attempt in student_attempts:
            if attempt.end_time and attempt.start_time:
                total_time += attempt.end_time - attempt.start_time
        
        avg_time = total_time.total_seconds() / total_attempts if total_attempts > 0 else 0
        avg_time_minutes = round(avg_time / 60, 1)
        
        student_stats.append({
            'student': student,
            'avg_score': avg_score,
            'total_attempts': total_attempts,
            'pass_rate': pass_rate,
            'best_quiz': best_quiz,
            'best_score': best_score,
            'avg_time_minutes': avg_time_minutes
        })
    
    # Sort by average score (descending)
    student_stats.sort(key=lambda x: x['avg_score'], reverse=True)
    
    # Add rank to each student
    for i, stat in enumerate(student_stats):
        stat['rank'] = i + 1
    
    # Calculate overall statistics
    total_attempts = attempts.count()
    avg_score_overall = attempts.aggregate(avg=Avg('score'))['avg'] or 0
    total_passed_overall = attempts.filter(score__gte=F('quiz__passing_score')).count()
    pass_rate_overall = (total_passed_overall / total_attempts * 100) if total_attempts > 0 else 0
    
    # Get quiz completion data for chart
    quiz_completion_data = []
    for quiz in quizzes:
        quiz_attempts = attempts.filter(quiz=quiz)
        total_quiz_attempts = quiz_attempts.count()
        if total_quiz_attempts > 0:
            avg_quiz_score = quiz_attempts.aggregate(avg=Avg('score'))['avg'] or 0
            quiz_completion_data.append({
                'quiz': quiz.title,
                'attempts': total_quiz_attempts,
                'avg_score': round(avg_quiz_score, 1)
            })
    
    # Get score distribution data for chart
    score_ranges = [
        {'range': '0-20%', 'count': attempts.filter(score__lt=20).count()},
        {'range': '21-40%', 'count': attempts.filter(score__gte=20, score__lt=40).count()},
        {'range': '41-60%', 'count': attempts.filter(score__gte=40, score__lt=60).count()},
        {'range': '61-80%', 'count': attempts.filter(score__gte=60, score__lt=80).count()},
        {'range': '81-100%', 'count': attempts.filter(score__gte=80).count()},
    ]
    
    context = {
        'student_stats': student_stats,
        'quizzes': quizzes,
        'selected_quiz': quiz_filter,
        'selected_period': time_period,
        'total_attempts': total_attempts,
        'avg_score_overall': round(avg_score_overall, 1),
        'pass_rate_overall': round(pass_rate_overall, 1),
        'quiz_completion_data': quiz_completion_data,
        'score_ranges': score_ranges,
    }
    
    return render(request, 'quiz/teacher/leaderboard.html', context)



# preview quiz
# Add this new view function for previewing quiz questions
@login_required
def preview_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    # Check if the user has permission to preview this question
    if not request.user.is_teacher or question.quiz.teacher.user != request.user:
        messages.error(request, "You don't have permission to preview this question.")
        return redirect('teacher_dashboard')
    
    # Determine question type and prepare context
    context = {
        'question': question,
        'quiz': question.quiz,
        'preview_mode': True,
    }
    
    return render(request, 'quiz/teacher/preview_question.html', context)



@login_required
def preview_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    # Check if the user has permission to preview this quiz
    if not request.user.is_teacher or quiz.teacher.user != request.user:
        messages.error(request, "You don't have permission to preview this quiz.")
        return redirect('teacher_dashboard')
    
    # Get all questions for this quiz
    questions = list(quiz.get_questions())
    
    # Apply shuffling if the quiz has that setting
    if quiz.shuffle_questions:
        import random
        random.shuffle(questions)
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'preview_mode': True,
        'time_limit_seconds': quiz.time_limit * 60,
        'prevent_tab_switch': quiz.prevent_tab_switch
    }
    
    return render(request, 'quiz/teacher/preview_quiz.html', context)