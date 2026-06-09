from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student-list'),
    path('generate-id/', views.generate_id, name='generate-id'),
    path('<int:pk>/', views.student_detail, name='student-detail'),
    path('<int:pk>/guardian/', views.add_guardian, name='add-guardian'),
]