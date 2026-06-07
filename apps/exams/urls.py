from django.urls import path
from . import views

urlpatterns = [
    path('', views.exam_list, name='exam-list'),
    path('<int:pk>/', views.exam_detail, name='exam-detail'),
    path('marks/', views.enter_bulk_marks, name='enter-bulk-marks'),
    path('<int:exam_id>/result/<int:student_id>/', views.result_card, name='result-card'),
]