from django.urls import path
from . import views

urlpatterns = [
    path('expenses/', views.expense_list, name='expense-list'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense-detail'),
    path('incomes/', views.income_list, name='income-list'),
    path('incomes/<int:pk>/', views.income_detail, name='income-detail'),
    path('summary/', views.summary, name='accounting-summary'),
    path('categories/', views.category_list, name='category-list'),
    path('salaries/', views.salary_list, name='salary-list'),
    path('salaries/<int:pk>/', views.salary_detail, name='salary-detail'),
    path('salary-teachers/', views.salary_teachers, name='salary-teachers'),
    path('ai-financial-health/', views.ai_financial_health, name='ai-financial-health'),
    path('ai-expense-optimization/', views.ai_expense_optimization, name='ai-expense-optimization'),
    path('ai-salary-report/', views.ai_salary_report, name='ai-salary-report'),
]