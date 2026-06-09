from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.academics.models import Class, Section, Subject
from apps.academics.serializers import ClassSerializer, SectionSerializer, SubjectSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def class_list(request):
    school = request.user.school
    classes = Class.objects.filter(school=school)
    return Response({'results': ClassSerializer(classes, many=True).data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def section_list(request):
    school = request.user.school
    class_id = request.query_params.get('class_id')
    sections = Section.objects.filter(school=school)
    if class_id:
        sections = sections.filter(class_name_id=class_id)
    return Response({'results': SectionSerializer(sections, many=True).data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subject_list(request):
    school = request.user.school
    class_id = request.query_params.get('class_id')
    subjects = Subject.objects.filter(school=school)
    if class_id:
        subjects = subjects.filter(class_name_id=class_id)
    return Response({'results': SubjectSerializer(subjects, many=True).data})