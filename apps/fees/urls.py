from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.category_list, name='fee-category-list'),
    path('payments/', views.payment_list, name='fee-payment-list'),
    path('payments/<int:pk>/', views.payment_detail, name='fee-payment-detail'),
    path('report/', views.fee_report, name='fee-report'),
    path('due/', views.due_list, name='fee-due-list'),
]