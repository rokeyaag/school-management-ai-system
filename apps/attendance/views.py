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
    role = request.user.role

    if role == 'student':
        try:
            student = Student.objects.get(user=request.user, school=school)
            attendances = Attendance.objects.filter(school=school, student=student)
            students = Student.objects.filter(id=student.id)
        except Student.DoesNotExist:
            return Response({'date': date, 'total_students': 0, 'marked': 0, 'results': []})
    else:
        attendances = Attendance.objects.filter(school=school, date=date)
        students = Student.objects.filter(school=school, is_active=True)

    serializer = AttendanceSerializer(attendances, many=True)
    return Response({
        'date': date,
        'total_students': students.count(),
        'marked': attendances.count(),
        'results': serializer.data,
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_bulk(request):
    if request.user.role == 'student':
        return Response({'error': 'Permission denied'}, status=403)
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
            if att_status == 'absent':
                try:
                    from apps.students.sms_service import send_absence_sms
                    send_absence_sms(student)
                except Exception as e:
                    print(f"SMS Error: {e}")
        except Student.DoesNotExist:
            continue
    return Response({'message': f'Attendance saved. Created: {created}, Updated: {updated}'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_report(request):
    school = request.user.school
    role = request.user.role
    attendances = Attendance.objects.filter(school=school)

    if role == 'student':
        try:
            student = Student.objects.get(user=request.user, school=school)
            attendances = attendances.filter(student=student)
        except Student.DoesNotExist:
            attendances = attendances.none()
    else:
        student_id = request.query_params.get('student_id')
        month = request.query_params.get('month')
        if student_id:
            attendances = attendances.filter(student_id=student_id)
        if month:
            attendances = attendances.filter(date__month=month)

    serializer = AttendanceSerializer(attendances, many=True)
    return Response({'results': serializer.data})