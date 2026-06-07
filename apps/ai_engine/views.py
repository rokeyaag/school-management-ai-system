from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .performance import analyze_student_performance
from .chatbot import school_chatbot


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_performance(request, student_id):
    lang = request.query_params.get('lang', 'en')
    result = analyze_student_performance(student_id, request.user.school, lang)
    if 'error' in result:
        return Response(result, status=status.HTTP_404_NOT_FOUND)
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chatbot(request):
    message = request.data.get('message', '')
    history = request.data.get('history', [])
    lang = request.data.get('lang', 'en')
    if not message:
        return Response({'error': 'message required'}, status=status.HTTP_400_BAD_REQUEST)
    result = school_chatbot(message, history, lang)
    return Response(result)