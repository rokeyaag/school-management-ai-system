from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Notice
from .serializers import NoticeSerializer
from apps.ai_engine.groq_client import chat

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def notice_list(request):
    school = request.user.school
    if request.method == 'GET':
        role = request.user.role
        notices = Notice.objects.filter(school=school, is_active=True)
        if role not in ['super_admin', 'school_admin']:
            notices = notices.filter(target_role__in=['all', role])
        return Response(NoticeSerializer(notices, many=True).data)
    serializer = NoticeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(school=school, created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def notice_detail(request, pk):
    notice = get_object_or_404(Notice, pk=pk, school=request.user.school)
    if request.method == 'GET':
        return Response(NoticeSerializer(notice).data)
    if request.method == 'PATCH':
        serializer = NoticeSerializer(notice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    notice.is_active = False
    notice.save()
    return Response({'message': 'Notice deleted'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_notice(request):
    topic = request.data.get('topic', '')
    lang = request.data.get('lang', 'en')
    school = request.user.school
    if lang == 'bn':
        prompt = f'You are a school AI assistant for {school.name}. Write a professional school notice in Bengali about "{topic}". Keep it formal and 3-4 sentences.'
    else:
        prompt = f'You are the AI assistant for {school.name}. Write a professional school notice about "{topic}". Keep it formal and concise (3-4 sentences).'
    messages = [{'role': 'user', 'content': prompt}]
    content = chat(messages)
    return Response({'content': content})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count(request):
    school = request.user.school
    role = request.user.role
    notices = Notice.objects.filter(school=school, is_active=True)
    if role not in ['super_admin', 'school_admin']:
        notices = notices.filter(target_role__in=['all', role])
    unread = notices.exclude(read_by=request.user).count()
    return Response({'count': unread})