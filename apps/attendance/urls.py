from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_list, name='attendance-list'),
    path('mark/', views.mark_bulk_attendance, name='mark-bulk-attendance'),
    path('report/', views.attendance_report, name='attendance-report'),
    path('<int:pk>/', views.update_attendance, name='update-attendance'),
]