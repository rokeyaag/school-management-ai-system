from django.urls import path
from apps.academics import views

urlpatterns = [
    path('classes/', views.class_list, name='class-list'),
    path('sections/', views.section_list, name='section-list'),
    path('subjects/', views.subject_list, name='subject-list'),
]