from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Exam, Marks
from .serializers import ExamSerializer, MarksSerializer, BulkMarksSerializer
from apps.students.models import Student
from apps.academics.models import Subject


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def exam_list(request):
    school = request.user.school
    if request.method == 'GET':
        exams = Exam.objects.filter(school=school)
        class_id = request.query_params.get('class_id')
        if class_id:
            exams = exams.filter(class_name_id=class_id)
        return Response(ExamSerializer(exams, many=True).data)

    serializer = ExamSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(school=school)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def exam_detail(request, pk):
    exam = get_object_or_404(Exam, pk=pk, school=request.user.school)
    if request.method == 'GET':
        return Response(ExamSerializer(exam).data)
    if request.method == 'PATCH':
        serializer = ExamSerializer(exam, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    exam.delete()
    return Response({'message': 'Exam deleted'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enter_bulk_marks(request):
    serializer = BulkMarksSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    exam = get_object_or_404(Exam, pk=data['exam_id'], school=request.user.school)
    created = updated = 0

    for item in data['marks']:
        student = Student.objects.filter(id=item['student_id'], school=request.user.school).first()
        subject = Subject.objects.filter(id=item['subject_id']).first()
        if not student or not subject:
            continue
        obj, is_created = Marks.objects.update_or_create(
            exam=exam, student=student, subject=subject,
            defaults={
                'marks_obtained': item.get('marks_obtained', 0),
                'total_marks': item.get('total_marks', 100),
                'is_absent': item.get('is_absent', False),
            }
        )
        if is_created:
            created += 1
        else:
            updated += 1

    return Response({'message': f'Marks saved. Created: {created}, Updated: {updated}'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def result_card(request, exam_id, student_id):
    school = request.user.school
    exam = get_object_or_404(Exam, pk=exam_id, school=school)
    student = get_object_or_404(Student, pk=student_id, school=school)
    marks_qs = Marks.objects.filter(exam=exam, student=student)

    subjects = []
    total_obtained = 0
    total_full = 0
    total_gp = 0

    for m in marks_qs:
        subjects.append({
            'subject': m.subject.name,
            'marks_obtained': float(m.marks_obtained),
            'total_marks': float(m.total_marks),
            'grade': m.grade,
            'grade_point': float(m.grade_point),
        })
        total_obtained += float(m.marks_obtained)
        total_full += float(m.total_marks)
        total_gp += float(m.grade_point)

    gpa = round(total_gp / len(subjects), 2) if subjects else 0
    result = 'Pass' if gpa >= 1.0 else 'Fail'

    # position
    all_students_marks = Marks.objects.filter(exam=exam).values('student').annotate(
        total=__import__('django.db.models', fromlist=['Sum']).Sum('marks_obtained')
    ).order_by('-total')
    position = 1
    for i, s in enumerate(all_students_marks):
        if s['student'] == student.id:
            position = i + 1
            break

    return Response({
        'student_id': student.id,
        'student_name': student.user.full_name,
        'student_roll': student.student_id,
        'exam_name': exam.name,
        'subjects': subjects,
        'total_marks': total_full,
        'obtained_marks': total_obtained,
        'gpa': gpa,
        'result': result,
        'position': position,
    })