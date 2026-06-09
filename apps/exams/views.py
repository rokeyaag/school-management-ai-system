from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Exam, Marks
from .serializers import ExamSerializer, MarksSerializer
from apps.students.models import Student
from apps.academics.models import Class, Subject


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def exam_list(request):
    school = request.user.school
    if request.method == 'GET':
        exams = Exam.objects.filter(school=school)
        return Response({'results': ExamSerializer(exams, many=True).data})
    data = request.data.copy()
    data['school'] = school.id
    serializer = ExamSerializer(data=data)
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


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def marks_list(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id, school=request.user.school)
    if request.method == 'GET':
        subject_id = request.query_params.get('subject')
        marks = Marks.objects.filter(exam=exam)
        if subject_id:
            marks = marks.filter(subject_id=subject_id)
        return Response({'results': MarksSerializer(marks, many=True).data})

    if request.method == 'POST':
        items = request.data.get('marks', [])
        saved = []
        for item in items:
            student_id = item.get('student')
            subject_id = item.get('subject')
            marks_obtained = item.get('marks_obtained', 0)
            total_marks = item.get('total_marks', 100)
            is_absent = item.get('is_absent', False)
            try:
                student = Student.objects.get(id=student_id)
                subject = Subject.objects.get(id=subject_id)
                obj, _ = Marks.objects.update_or_create(
                    exam=exam, student=student, subject=subject,
                    defaults={
                        'marks_obtained': marks_obtained,
                        'total_marks': total_marks,
                        'is_absent': is_absent,
                    }
                )
                saved.append(obj.id)
            except Exception:
                continue
        return Response({'message': f'{len(saved)} marks saved'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def result_card(request, exam_id, student_id):
    exam = get_object_or_404(Exam, pk=exam_id, school=request.user.school)
    student = get_object_or_404(Student, pk=student_id, school=request.user.school)
    marks = Marks.objects.filter(exam=exam, student=student)

    total_obtained = sum(float(m.marks_obtained) for m in marks if not m.is_absent)
    total_full = sum(float(m.total_marks) for m in marks)
    avg_gpa = sum(float(m.grade_point) for m in marks) / len(marks) if marks else 0

    return Response({
        'student': {
            'name': student.user.full_name,
            'student_id': student.student_id,
            'roll': student.roll,
            'photo': student.photo,
        },
        'exam': ExamSerializer(exam).data,
        'marks': MarksSerializer(marks, many=True).data,
        'summary': {
            'total_obtained': total_obtained,
            'total_full': total_full,
            'percentage': round((total_obtained / total_full * 100), 2) if total_full else 0,
            'gpa': round(avg_gpa, 2),
        }
    })