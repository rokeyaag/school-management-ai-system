from django.urls import path
from . import views

urlpatterns = [
    path('performance/<int:student_id>/', views.student_performance, name='ai-performance'),
    path('chatbot/', views.chatbot, name='ai-chatbot'),
    path('lesson-plan/', views.lesson_plan, name='ai-lesson-plan'),
    path('study-recommendation/', views.study_recommendation, name='ai-study-recommendation'),
    path('school-health/', views.school_health, name='ai-school-health'),
]