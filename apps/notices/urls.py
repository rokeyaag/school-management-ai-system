from django.urls import path
from . import views

urlpatterns = [
    path('', views.notice_list, name='notice-list'),
    path('generate/', views.generate_notice, name='generate-notice'),
    path('unread-count/', views.unread_count, name='unread-count'),
    path('<int:pk>/', views.notice_detail, name='notice-detail'),
]