from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_school, name='register-school'),
    path('schools/', views.school_list, name='school-list'),
    path('schools/<str:school_id>/approve/', views.approve_school, name='approve-school'),
]