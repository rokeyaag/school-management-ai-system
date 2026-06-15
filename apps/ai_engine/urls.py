from django.urls import path
from . import views
urlpatterns = [
    path('performance/<int:student_id>/', views.student_performance, name='ai-performance'),
    path('chatbot/', views.chatbot, name='ai-chatbot'),
    path('lesson-plan/', views.lesson_plan, name='ai-lesson-plan'),
    path('study-recommendation/', views.study_recommendation, name='ai-study-recommendation'),
    path('school-health/', views.school_health, name='ai-school-health'),
    path('question-generator/', views.question_generator, name='ai-question-generator'),
    path('attendance-predictor/', views.attendance_predictor, name='ai-attendance-predictor'),
    path('fee-defaulter/', views.fee_defaulter, name='ai-fee-defaulter'),
    path('parent-report/', views.parent_progress_report, name='ai-parent-report'),
]