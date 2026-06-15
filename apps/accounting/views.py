from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Expense, ExpenseCategory, Income
from django.utils import timezone

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def expense_list(request):
    school = request.user.school
    if request.method == 'GET':
        expenses = Expense.objects.filter(school=school).select_related('category', 'added_by')
        data = [{'id': e.id, 'title': e.title, 'amount': float(e.amount), 'date': e.date, 'category': e.category.name if e.category else 'Uncategorized', 'payment_method': e.payment_method, 'note': e.note} for e in expenses]
        return Response(data)
    category_id = request.data.get('category')
    expense = Expense.objects.create(school=school, title=request.data.get('title'), amount=request.data.get('amount'), date=request.data.get('date'), category_id=category_id if category_id else None, payment_method=request.data.get('payment_method', 'cash'), note=request.data.get('note', ''), added_by=request.user)
    return Response({'id': expense.id, 'message': 'Expense added'}, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def expense_detail(request, pk):
    try:
        expense = Expense.objects.get(id=pk, school=request.user.school)
        expense.delete()
        return Response({'message': 'Deleted'})
    except Expense.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def income_list(request):
    school = request.user.school
    if request.method == 'GET':
        incomes = Income.objects.filter(school=school).select_related('added_by')
        data = [{'id': i.id, 'title': i.title, 'amount': float(i.amount), 'date': i.date, 'source': i.source, 'note': i.note} for i in incomes]
        return Response(data)
    income = Income.objects.create(school=school, title=request.data.get('title'), amount=request.data.get('amount'), date=request.data.get('date'), source=request.data.get('source', 'other'), note=request.data.get('note', ''), added_by=request.user)
    return Response({'id': income.id, 'message': 'Income added'}, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def income_detail(request, pk):
    try:
        income = Income.objects.get(id=pk, school=request.user.school)
        income.delete()
        return Response({'message': 'Deleted'})
    except Income.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def summary(request):
    school = request.user.school
    all_time = request.query_params.get('all', 'false')
    month = request.query_params.get('month', timezone.now().month)
    year = request.query_params.get('year', timezone.now().year)

    if all_time == 'true':
        expenses = Expense.objects.filter(school=school)
        incomes = Income.objects.filter(school=school)
        from apps.fees.models import FeePayment
        fee_payments = FeePayment.objects.filter(school=school, status='paid')
    else:
        expenses = Expense.objects.filter(school=school, date__month=month, date__year=year)
        incomes = Income.objects.filter(school=school, date__month=month, date__year=year)
        from apps.fees.models import FeePayment
        fee_payments = FeePayment.objects.filter(school=school, status='paid', paid_date__month=month, paid_date__year=year)

    total_expense = float(sum(e.amount for e in expenses))
    total_other_income = float(sum(i.amount for i in incomes))
    total_fee = float(sum(f.amount for f in fee_payments))
    total_income = total_other_income + total_fee

    return Response({
        'total_expense': round(total_expense, 2),
        'total_income': round(total_income, 2),
        'fee_income': round(total_fee, 2),
        'other_income': round(total_other_income, 2),
        'profit': round(total_income - total_expense, 2),
        'expense_count': expenses.count(),
        'income_count': incomes.count(),
    })

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def category_list(request):
    school = request.user.school
    if request.method == 'GET':
        cats = ExpenseCategory.objects.filter(school=school)
        return Response([{'id': c.id, 'name': c.name} for c in cats])
    cat = ExpenseCategory.objects.create(school=school, name=request.data.get('name'), description=request.data.get('description', ''))
    return Response({'id': cat.id, 'name': cat.name}, status=status.HTTP_201_CREATED)