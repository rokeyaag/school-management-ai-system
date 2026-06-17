from django.urls import path
from apps.academics import views
from apps.academics import timetable_views

urlpatterns = [
    path('classes/', views.class_list, name='class-list'),
    path('sections/', views.section_list, name='section-list'),
    path('subjects/', views.subject_list, name='subject-list'),
    path('timetable/', timetable_views.timetable_list, name='timetable-list'),
    path('timetable/<int:pk>/', timetable_views.timetable_detail, name='timetable-detail'),
]