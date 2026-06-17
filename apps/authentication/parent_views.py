from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.students.models import Student
from apps.attendance.models import Attendance
from apps.exams.models import Marks, Exam
from apps.fees.models import FeePayment
from apps.notices.models import Notice
from apps.authentication.models import CustomUser
from apps.tenants.models import School


def get_school(user):
    if user.school:
        return user.school
    return School.objects.filter(name="Dhaka Model School").first()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def parent_dashboard(request):
    user = request.user
    school = get_school(user)

    # Find children via guardian mobile or father/mother mobile
    children = Student.objects.filter(
        school=school
    ).filter(
        father_mobile=user.phone
    ) | Student.objects.filter(
        school=school
    ).filter(
        mother_mobile=user.phone
    ) | Student.objects.filter(
        school=school,
        guardians__user=user
    )
    children = children.distinct().select_related('user', 'class_name')

    data = []
    for student in children:
        # Attendance
        att = Attendance.objects.filter(student=student).order_by('-date')
        total = att.count()
        present = att.filter(status='present').count()
        att_pct = round((present / total) * 100, 1) if total > 0 else 0

        # Latest exam marks
        latest_marks = Marks.objects.filter(student=student).select_related('subject', 'exam').order_by('-created_at')[:10]

        # Fee status
        fees = FeePayment.objects.filter(student=student).order_by('-created_at')[:5]

        data.append({
            'id': student.id,
            'name': student.user.full_name,
            'student_id': student.student_id,
            'class_name': student.class_name.name if student.class_name else '-',
            'roll': student.roll,
            'photo': student.photo or '',
            'attendance_pct': att_pct,
            'attendance_present': present,
            'attendance_total': total,
            'marks': [
                {
                    'subject': m.subject.name,
                    'exam': m.exam.name,
                    'obtained': float(m.marks_obtained),
                    'total': float(m.total_marks),
                    'grade': m.grade,
                    'grade_point': float(m.grade_point),
                }
                for m in latest_marks
            ],
            'fees': [
                {
                    'amount': float(f.amount),
                    'status': f.status,
                    'date': str(f.payment_date or f.created_at.date()),
                    'method': f.payment_method,
                }
                for f in fees
            ],
        })

    # Notices
    notices = Notice.objects.filter(school=school, is_active=True).order_by('-created_at')[:5]

    return Response({
        'children': data,
        'notices': [
            {'title': n.title, 'content': n.content[:200], 'date': str(n.created_at.date())}
            for n in notices
        ]
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_parent(request):
    """Create parent account linked to student by mobile"""
    school = get_school(request.user)
    data = request.data

    email = data.get('email', '').strip()
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '').strip()
    student_id = data.get('student_id', '').strip()

    if not all([email, full_name, phone, password, student_id]):
        return Response({'error': 'All fields required'}, status=status.HTTP_400_BAD_REQUEST)

    if CustomUser.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        student = Student.objects.get(student_id=student_id, school=school)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    user = CustomUser.objects.create_user(
        email=email,
        full_name=full_name,
        phone=phone,
        password=password,
        role='parent',
        school=school
    )

    return Response({
        'message': 'Parent account created successfully',
        'email': email,
        'linked_student': student.user.full_name,
    }, status=status.HTTP_201_CREATED)