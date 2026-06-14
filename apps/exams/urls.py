from django.urls import path
from . import views

urlpatterns = [
    path('', views.exam_list, name='exam-list'),
    path('<int:pk>/', views.exam_detail, name='exam-detail'),
    path('<int:pk>/publish/', views.publish_exam, name='publish-exam'),
    path('<int:exam_id>/results/', views.result_list, name='result-list'),
    path('<int:exam_id>/results/<int:result_id>/', views.result_update, name='result-update'),
    path('<int:exam_id>/report-card/', views.generate_report_card, name='generate-report-card'),
]