from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Teacher
from .serializers import TeacherSerializer, TeacherCreateSerializer
from apps.authentication.models import CustomUser


def generate_employee_id(school):
    last = Teacher.objects.filter(school=school).order_by('-created_at').first()
    if last and last.employee_id.startswith('TCH-'):
        try:
            num = int(last.employee_id.split('-')[1]) + 1
        except:
            num = 1
    else:
        num = 1
    return f'TCH-{num:04d}'


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def teacher_list(request):
    if request.method == 'GET':
        school = request.user.school
        if not school:
            return Response({'error': 'No school assigned'}, status=status.HTTP_403_FORBIDDEN)
        teachers = Teacher.objects.filter(school=school, is_active=True)
        search = request.query_params.get('search')
        if search:
            teachers = teachers.filter(user__full_name__icontains=search) | teachers.filter(employee_id__icontains=search)
        serializer = TeacherSerializer(teachers, many=True)
        return Response({'count': teachers.count(), 'results': serializer.data})

    if request.method == 'POST':
        serializer = TeacherCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            school = request.user.school
            if not school:
                return Response({'error': 'No school assigned'}, status=status.HTTP_403_FORBIDDEN)
            user = CustomUser.objects.create_user(
                email=data['email'],
                full_name=data['full_name'],
                phone=data.get('phone', ''),
                password=data['password'],
                role='teacher',
                school=school
            )
            if data.get('avatar'):
                user.avatar = data['avatar']
                user.save()
            employee_id = data.get('employee_id') or generate_employee_id(school)
            teacher = Teacher.objects.create(
                user=user, school=school,
                employee_id=employee_id,
                specialization=data.get('specialization', ''),
                qualification=data.get('qualification', ''),
                join_date=data.get('join_date'),
                salary=data.get('salary'),
            )
            return Response(TeacherSerializer(teacher).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk, school=request.user.school)
    if request.method == 'GET':
        return Response(TeacherSerializer(teacher).data)
    if request.method == 'PATCH':
        data = request.data
        user = teacher.user
        for field in ['full_name', 'phone', 'avatar']:
            if field in data:
                setattr(user, field, data[field])
        user.save()
        for field in ['specialization', 'qualification', 'join_date', 'salary']:
            if field in data:
                setattr(teacher, field, data[field])
        teacher.save()
        return Response(TeacherSerializer(teacher).data)
    teacher.is_active = False
    teacher.save()
    return Response({'message': 'Teacher deactivated'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_id(request):
    school = request.user.school
    return Response({'employee_id': generate_employee_id(school)})