from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Class, Section, Subject, Timetable
from apps.teachers.models import Teacher
from apps.tenants.models import School


def get_school(user):
    if user.school:
        return user.school
    return School.objects.filter(name="Dhaka Model School").first()


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def timetable_list(request):
    school = get_school(request.user)
    if request.method == 'GET':
        section_id = request.query_params.get('section_id')
        class_id = request.query_params.get('class_id')
        if section_id:
            entries = Timetable.objects.filter(section_id=section_id).select_related('subject', 'teacher__user', 'section__class_name')
        elif class_id:
            entries = Timetable.objects.filter(section__class_name_id=class_id, section__school=school).select_related('subject', 'teacher__user', 'section__class_name')
        else:
            entries = Timetable.objects.filter(section__school=school).select_related('subject', 'teacher__user', 'section__class_name')

        data = []
        for e in entries:
            data.append({
                'id': e.id,
                'day': e.day,
                'start_time': str(e.start_time)[:5],
                'end_time': str(e.end_time)[:5],
                'subject': e.subject.name,
                'subject_id': e.subject.id,
                'teacher': e.teacher.user.full_name,
                'teacher_id': e.teacher.id,
                'section': e.section.name,
                'section_id': e.section.id,
                'class_name': e.section.class_name.name,
            })
        return Response(data)

    if request.method == 'POST':
        try:
            entry = Timetable.objects.create(
                section_id=request.data['section_id'],
                subject_id=request.data['subject_id'],
                teacher_id=request.data['teacher_id'],
                day=request.data['day'],
                start_time=request.data['start_time'],
                end_time=request.data['end_time'],
            )
            return Response({'id': entry.id, 'message': 'Created'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def timetable_detail(request, pk):
    try:
        entry = Timetable.objects.get(pk=pk)
        entry.delete()
        return Response({'message': 'Deleted'})
    except Timetable.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)