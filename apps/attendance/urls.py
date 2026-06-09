from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_list, name='attendance-list'),
    path('mark/', views.mark_bulk, name='attendance-mark'),
    path('report/', views.attendance_report, name='attendance-report'),
]