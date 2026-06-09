from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import date as today_date
from .models import Attendance
from .serializers import AttendanceSerializer
from apps.students.models import Student


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_list(request):
    school = request.user.school
    date = request.query_params.get('date', str(today_date.today()))
    attendances = Attendance.objects.filter(school=school, date=date)
    serializer = AttendanceSerializer(attendances, many=True)

    # Get all students
    students = Student.objects.filter(school=school, is_active=True)
    marked_ids = [a.student_id for a in attendances]

    return Response({
        'date': date,
        'total_students': students.count(),
        'marked': attendances.count(),
        'results': serializer.data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_bulk(request):
    school = request.user.school
    date = request.data.get('date', str(today_date.today()))
    attendances = request.data.get('attendances', [])

    created = 0
    updated = 0
    for item in attendances:
        student_id = item.get('student')
        att_status = item.get('status', 'present')
        note = item.get('note', '')
        try:
            student = Student.objects.get(id=student_id, school=school)
            obj, created_flag = Attendance.objects.update_or_create(
                student=student, date=date,
                defaults={'status': att_status, 'note': note, 'school': school}
            )
            if created_flag:
                created += 1
            else:
                updated += 1
        except Student.DoesNotExist:
            continue

    return Response({'message': f'Attendance saved. Created: {created}, Updated: {updated}'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_report(request):
    school = request.user.school
    student_id = request.query_params.get('student_id')
    month = request.query_params.get('month')

    attendances = Attendance.objects.filter(school=school)
    if student_id:
        attendances = attendances.filter(student_id=student_id)
    if month:
        attendances = attendances.filter(date__month=month)

    serializer = AttendanceSerializer(attendances, many=True)
    return Response({'results': serializer.data})