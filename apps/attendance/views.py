from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from .models import Attendance
from .serializers import AttendanceSerializer, BulkAttendanceSerializer
from apps.students.models import Student
from apps.academics.models import Section


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_list(request):
    school = request.user.school
    attendances = Attendance.objects.filter(school=school)
    date = request.query_params.get('date')
    section_id = request.query_params.get('section_id')
    student_id = request.query_params.get('student_id')
    if date:
        attendances = attendances.filter(date=date)
    if section_id:
        attendances = attendances.filter(section_id=section_id)
    if student_id:
        attendances = attendances.filter(student_id=student_id)
    serializer = AttendanceSerializer(attendances, many=True)
    return Response({'count': attendances.count(), 'results': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_bulk_attendance(request):
    serializer = BulkAttendanceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    school = request.user.school
    date = data['date']
    section_id = data['section_id']
    attendances_data = data['attendances']

    teacher = getattr(request.user, 'teacher_profile', None)
    created_count = 0
    updated_count = 0

    for item in attendances_data:
        student = Student.objects.filter(id=item['student_id'], school=school).first()
        if not student:
            continue
        obj, created = Attendance.objects.update_or_create(
            student=student,
            date=date,
            defaults={
                'school': school,
                'section_id': section_id,
                'marked_by': teacher,
                'status': item['status'],
                'note': item.get('note', ''),
            }
        )
        if created:
            created_count += 1
        else:
            updated_count += 1

    return Response({
        'message': f'Attendance saved. Created: {created_count}, Updated: {updated_count}'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_report(request):
    school = request.user.school
    student_id = request.query_params.get('student_id')
    month = request.query_params.get('month')
    year = request.query_params.get('year')

    students = Student.objects.filter(school=school, is_active=True)
    if student_id:
        students = students.filter(id=student_id)

    report = []
    for student in students:
        qs = Attendance.objects.filter(student=student, school=school)
        if month:
            qs = qs.filter(date__month=month)
        if year:
            qs = qs.filter(date__year=year)

        total = qs.count()
        present = qs.filter(status='present').count()
        absent = qs.filter(status='absent').count()
        late = qs.filter(status='late').count()
        excused = qs.filter(status='excused').count()
        percentage = round((present / total * 100), 2) if total > 0 else 0

        report.append({
            'student_id': student.id,
            'student_name': student.user.full_name,
            'total_days': total,
            'present': present,
            'absent': absent,
            'late': late,
            'excused': excused,
            'percentage': percentage,
        })

    return Response(report)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_attendance(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk, school=request.user.school)
    serializer = AttendanceSerializer(attendance, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)