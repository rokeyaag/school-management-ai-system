from django.urls import path
from . import views

urlpatterns = [
    path('', views.teacher_list, name='teacher-list'),
    path('generate-id/', views.generate_id, name='teacher-generate-id'),
    path('<int:pk>/', views.teacher_detail, name='teacher-detail'),
]