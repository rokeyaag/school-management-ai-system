from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Exam, Marks
from .serializers import ExamSerializer, MarksSerializer
from apps.ai_engine.groq_client import chat

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def exam_list(request):
    school = request.user.school
    if request.method == 'GET':
        exams = Exam.objects.filter(school=school)
        return Response(ExamSerializer(exams, many=True).data)
    serializer = ExamSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(school=school)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def exam_detail(request, pk):
    try:
        exam = Exam.objects.get(pk=pk, school=request.user.school)
    except Exam.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(ExamSerializer(exam).data)
    if request.method == 'PATCH':
        serializer = ExamSerializer(exam, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    exam.delete()
    return Response({'message': 'Deleted'})

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def result_list(request, exam_id):
    school = request.user.school
    if request.method == 'GET':
        results = Marks.objects.filter(exam__school=school, exam_id=exam_id)
        return Response(MarksSerializer(results, many=True).data)
    serializer = MarksSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def result_update(request, exam_id, result_id):
    try:
        result = Marks.objects.get(pk=result_id, exam_id=exam_id, exam__school=request.user.school)
        serializer = MarksSerializer(result, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Marks.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def publish_exam(request, pk):
    try:
        exam = Exam.objects.get(pk=pk, school=request.user.school)
        exam.is_published = not exam.is_published
        exam.save()
        return Response({'is_published': exam.is_published})
    except Exam.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_report_card(request, exam_id):
    try:
        exam = Exam.objects.get(pk=exam_id, school=request.user.school)
    except Exam.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    results = Marks.objects.filter(exam=exam)
    if not results.exists():
        return Response({'error': 'No results found'}, status=status.HTTP_400_BAD_REQUEST)
    student_id = request.data.get('student_id')
    if student_id:
        results = results.filter(student_id=student_id)
    report_data = []
    for r in results:
        report_data.append(f"{r.student.full_name if hasattr(r.student, 'full_name') else r.student}: {r.subject.name} - {r.marks_obtained}/{r.total_marks} ({r.grade})")
    summary = "\n".join(report_data)
    prompt = f"You are a school teacher at {exam.school.name}. Based on the following exam results for {exam.name}, write a professional report card comment for each student. Be encouraging and constructive.\n\nResults:\n{summary}\n\nWrite individual comments for each student."
    messages = [{'role': 'user', 'content': prompt}]
    content = chat(messages)
    return Response({'report': content, 'exam': exam.name})