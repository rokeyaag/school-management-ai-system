from django.urls import path
from . import views

urlpatterns = [
    path('expenses/', views.expense_list, name='expense-list'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense-detail'),
    path('incomes/', views.income_list, name='income-list'),
    path('incomes/<int:pk>/', views.income_detail, name='income-detail'),
    path('summary/', views.summary, name='accounting-summary'),
    path('categories/', views.category_list, name='category-list'),
]