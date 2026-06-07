from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from .models import FeeCategory, FeeSchedule, FeePayment
from .serializers import FeeCategorySerializer, FeeScheduleSerializer, FeePaymentSerializer
from apps.students.models import Student


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def category_list(request):
    school = request.user.school
    if request.method == 'GET':
        categories = FeeCategory.objects.filter(school=school, is_active=True)
        return Response(FeeCategorySerializer(categories, many=True).data)
    serializer = FeeCategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(school=school)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def payment_list(request):
    school = request.user.school
    if request.method == 'GET':
        payments = FeePayment.objects.filter(school=school)
        student_id = request.query_params.get('student_id')
        status_filter = request.query_params.get('status')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        if student_id:
            payments = payments.filter(student_id=student_id)
        if status_filter:
            payments = payments.filter(status=status_filter)
        if month:
            payments = payments.filter(month=month)
        if year:
            payments = payments.filter(year=year)
        return Response({
            'count': payments.count(),
            'results': FeePaymentSerializer(payments, many=True).data
        })

    serializer = FeePaymentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(school=school)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def payment_detail(request, pk):
    payment = get_object_or_404(FeePayment, pk=pk, school=request.user.school)
    serializer = FeePaymentSerializer(payment, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fee_report(request):
    school = request.user.school
    student_id = request.query_params.get('student_id')
    students = Student.objects.filter(school=school, is_active=True)
    if student_id:
        students = students.filter(id=student_id)

    report = []
    for student in students:
        payments = FeePayment.objects.filter(student=student, school=school)
        total = payments.aggregate(t=Sum('amount'))['t'] or 0
        paid = payments.filter(status='paid').aggregate(p=Sum('paid_amount'))['p'] or 0
        due = float(total) - float(paid)
        report.append({
            'student_id': student.id,
            'student_name': student.user.full_name,
            'total_amount': float(total),
            'paid_amount': float(paid),
            'due_amount': due,
        })
    return Response(report)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def due_list(request):
    school = request.user.school
    due_payments = FeePayment.objects.filter(school=school, status='due')
    return Response({
        'count': due_payments.count(),
        'results': FeePaymentSerializer(due_payments, many=True).data
    })