from django.urls import path
from . import views

urlpatterns = [
    path('', views.exam_list, name='exam-list'),
    path('<int:pk>/', views.exam_detail, name='exam-detail'),
    path('<int:exam_id>/marks/', views.marks_list, name='marks-list'),
    path('<int:exam_id>/result/<int:student_id>/', views.result_card, name='result-card'),
]