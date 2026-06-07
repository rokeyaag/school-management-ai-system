from django.urls import path
from . import views

urlpatterns = [
    path('performance/<int:student_id>/', views.student_performance, name='ai-performance'),
    path('chatbot/', views.chatbot, name='ai-chatbot'),
]