from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Expense, ExpenseCategory, Income, SalaryPayment
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
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def salary_list(request):
    school = request.user.school
    if request.method == 'GET':
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        salaries = SalaryPayment.objects.filter(school=school).select_related('teacher__user')
        if month and year:
            salaries = salaries.filter(month=month, year=year)
        data = [{
            'id': s.id,
            'teacher_id': s.teacher.id,
            'teacher_name': s.teacher.user.full_name,
            'employee_id': s.teacher.employee_id,
            'month': s.month,
            'year': s.year,
            'amount': float(s.amount),
            'paid_amount': float(s.paid_amount),
            'status': s.status,
            'payment_method': s.payment_method,
            'payment_date': s.payment_date,
        } for s in salaries]
        return Response(data)
    # POST
    teacher_id = request.data.get('teacher_id')
    month = request.data.get('month')
    year = request.data.get('year')
    amount = request.data.get('amount')
    salary, created = SalaryPayment.objects.update_or_create(
        teacher_id=teacher_id, month=month, year=year,
        defaults={
            'school': school,
            'amount': amount,
            'paid_amount': request.data.get('paid_amount', amount),
            'status': request.data.get('status', 'paid'),
            'payment_method': request.data.get('payment_method', 'cash'),
            'payment_date': request.data.get('payment_date'),
            'note': request.data.get('note', ''),
            'paid_by': request.user,
        }
    )
    return Response({'id': salary.id, 'message': 'Salary saved'}, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def salary_detail(request, pk):
    try:
        salary = SalaryPayment.objects.get(id=pk, school=request.user.school)
        salary.delete()
        return Response({'message': 'Deleted'})
    except SalaryPayment.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def salary_teachers(request):
    school = request.user.school
    from apps.teachers.models import Teacher
    teachers = Teacher.objects.filter(school=school, is_active=True).select_related('user')
    return Response([{'id': t.id, 'name': t.user.full_name, 'employee_id': t.employee_id, 'salary': float(t.salary) if t.salary else 0} for t in teachers])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_financial_report(request):
    lang = request.query_params.get('lang', 'en')
    month = request.query_params.get('month', timezone.now().month)
    year = request.query_params.get('year', timezone.now().year)
    school = request.user.school

    expenses = Expense.objects.filter(school=school, date__month=month, date__year=year)
    incomes = Income.objects.filter(school=school, date__month=month, date__year=year)
    from apps.fees.models import FeePayment
    fee_payments = FeePayment.objects.filter(school=school, status='paid', paid_date__month=month, paid_date__year=year)
    salaries = SalaryPayment.objects.filter(school=school, month=month, year=year)

    total_expense = float(sum(e.amount for e in expenses))
    total_other_income = float(sum(i.amount for i in incomes))
    total_fee = float(sum(f.amount for f in fee_payments))
    total_income = total_other_income + total_fee
    total_salary_paid = float(sum(s.paid_amount for s in salaries.filter(status='paid')))
    total_salary_pending = salaries.filter(status='pending').count()

    expense_by_category = {}
    for e in expenses:
        cat = e.category.name if e.category else 'Uncategorized'
        expense_by_category[cat] = expense_by_category.get(cat, 0) + float(e.amount)
    expense_breakdown = '\n'.join([f"- {k}: ৳{v}" for k, v in expense_by_category.items()]) or 'No expenses'

    profit = total_income - total_expense - total_salary_paid

    if lang == 'bn':
        prompt = f'''তুমি {school.name} এর একজন financial analyst। নিচের মাসিক financial data বিশ্লেষণ করে বাংলায় একটি বিস্তারিত financial health report দাও।

মোট আয়:
ফি থেকে: ৳{total_fee}
অন্যান্য: ৳{total_other_income}
সর্বমোট: ৳{total_income}

মোট খরচ: ৳{total_expense}
খরচের বিভাজন:
{expense_breakdown}

বেতন:
পরিশোধিত: ৳{total_salary_paid}
বকেয়া: {total_salary_pending} জন

নিট লাভ/ক্ষতি: ৳{profit}

প্রদান করো:
১) সামগ্রিক আর্থিক স্বাস্থ্য মূল্যায়ন
২) আয়-ব্যয় বিশ্লেষণ
৩) ঝুঁকি ও সতর্কতা (যদি থাকে)
৪) সাশ্রয়ের পরামর্শ
৫) পরবর্তী মাসের জন্য সুপারিশ'''
    else:
        prompt = f'''You are a financial analyst for {school.name}. Analyze this monthly financial data and provide a comprehensive financial health report.

Total Income:
From Fees: ৳{total_fee}
Other Income: ৳{total_other_income}
Total: ৳{total_income}

Total Expenses: ৳{total_expense}
Expense Breakdown:
{expense_breakdown}

Salaries:
Paid: ৳{total_salary_paid}
Pending: {total_salary_pending} teachers

Net Profit/Loss: ৳{profit}

Provide:
1) Overall financial health assessment
2) Income vs Expense analysis
3) Risk factors & warnings (if any)
4) Cost-saving recommendations
5) Suggestions for next month'''

    messages = [{'role': 'user', 'content': prompt}]
    from apps.ai_engine.groq_client import chat
    result = chat(messages)
    return Response({
        'report': result,
        'summary': {
            'total_income': round(total_income, 2),
            'total_expense': round(total_expense, 2),
            'total_salary_paid': round(total_salary_paid, 2),
            'salary_pending': total_salary_pending,
            'profit': round(profit, 2),
            'expense_breakdown': expense_by_category,
        }
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_financial_health(request):
    lang = request.query_params.get('lang', 'en')
    month = request.query_params.get('month', timezone.now().month)
    year = request.query_params.get('year', timezone.now().year)
    school = request.user.school
    expenses = Expense.objects.filter(school=school, date__month=month, date__year=year)
    incomes = Income.objects.filter(school=school, date__month=month, date__year=year)
    from apps.fees.models import FeePayment
    fee_payments = FeePayment.objects.filter(school=school, status='paid', paid_date__month=month, paid_date__year=year)
    total_expense = float(sum(e.amount for e in expenses))
    total_other_income = float(sum(i.amount for i in incomes))
    total_fee = float(sum(f.amount for f in fee_payments))
    total_income = total_other_income + total_fee
    profit = total_income - total_expense

    if lang == 'bn':
        prompt = f'তুমি {school.name} এর financial analyst। এই মাসের আয় ৳{total_income} (ফি: ৳{total_fee}, অন্যান্য: ৳{total_other_income}), খরচ ৳{total_expense}, নিট লাভ ৳{profit}। বাংলায় একটি সামগ্রিক আর্থিক স্বাস্থ্য মূল্যায়ন রিপোর্ট দাও যাতে থাকবে: ১) overall health score ২) মূল পর্যবেক্ষণ ৩) ঝুঁকি সতর্কতা ৪) সুপারিশ।'
    else:
        prompt = f'You are a financial analyst for {school.name}. This month income ৳{total_income} (fees: ৳{total_fee}, other: ৳{total_other_income}), expense ৳{total_expense}, net profit ৳{profit}. Provide an overall financial health report with: 1) Health score 2) Key observations 3) Risk warnings 4) Recommendations.'
    from apps.ai_engine.groq_client import chat
    result = chat([{'role': 'user', 'content': prompt}])
    return Response({'report': result, 'summary': {'total_income': total_income, 'total_expense': total_expense, 'profit': profit}})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_expense_optimization(request):
    lang = request.query_params.get('lang', 'en')
    month = request.query_params.get('month', timezone.now().month)
    year = request.query_params.get('year', timezone.now().year)
    school = request.user.school
    expenses = Expense.objects.filter(school=school, date__month=month, date__year=year)
    expense_by_category = {}
    for e in expenses:
        cat = e.category.name if e.category else 'Uncategorized'
        expense_by_category[cat] = expense_by_category.get(cat, 0) + float(e.amount)
    breakdown = '\n'.join([f"- {k}: ৳{v}" for k, v in expense_by_category.items()]) or 'No expenses'
    total = sum(expense_by_category.values())

    if lang == 'bn':
        prompt = f'তুমি {school.name} এর cost analyst। এই মাসের মোট খরচ ৳{total}। বিভাজন:\n{breakdown}\n\nবাংলায় একটি expense optimization রিপোর্ট দাও: ১) কোন খাতে সবচেয়ে বেশি খরচ ২) সাশ্রয়ের সুযোগ ৩) বাস্তবসম্মত পরামর্শ।'
    else:
        prompt = f'You are a cost analyst for {school.name}. Total expense this month ৳{total}. Breakdown:\n{breakdown}\n\nProvide an expense optimization report: 1) Highest spending areas 2) Cost-saving opportunities 3) Practical recommendations.'
    from apps.ai_engine.groq_client import chat
    result = chat([{'role': 'user', 'content': prompt}])
    return Response({'report': result, 'breakdown': expense_by_category, 'total': total})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_salary_report(request):
    lang = request.query_params.get('lang', 'en')
    month = request.query_params.get('month', timezone.now().month)
    year = request.query_params.get('year', timezone.now().year)
    school = request.user.school
    from apps.teachers.models import Teacher
    teachers = Teacher.objects.filter(school=school, is_active=True)
    salaries = SalaryPayment.objects.filter(school=school, month=month, year=year)
    total_paid = float(sum(s.paid_amount for s in salaries.filter(status='paid')))
    paid_count = salaries.filter(status='paid').count()
    pending_count = teachers.count() - paid_count
    total_staff = teachers.count()
    avg_salary = total_paid / paid_count if paid_count > 0 else 0

    if lang == 'bn':
        prompt = f'তুমি {school.name} এর HR/payroll analyst। মোট শিক্ষক {total_staff} জন। এই মাসে বেতন পরিশোধ হয়েছে {paid_count} জনের (মোট ৳{total_paid}), বাকি আছে {pending_count} জনের। গড় বেতন ৳{round(avg_salary,2)}। বাংলায় একটি salary ও staff cost রিপোর্ট দাও: ১) payroll স্বাস্থ্য ২) বকেয়া ঝুঁকি ৩) সুপারিশ।'
    else:
        prompt = f'You are an HR/payroll analyst for {school.name}. Total {total_staff} teachers. This month {paid_count} paid (total ৳{total_paid}), {pending_count} pending. Average salary ৳{round(avg_salary,2)}. Provide a salary & staff cost report: 1) Payroll health 2) Pending salary risks 3) Recommendations.'
    from apps.ai_engine.groq_client import chat
    result = chat([{'role': 'user', 'content': prompt}])
    return Response({'report': result, 'summary': {'total_staff': total_staff, 'paid_count': paid_count, 'pending_count': pending_count, 'total_paid': total_paid, 'avg_salary': round(avg_salary,2)}})