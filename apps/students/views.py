from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Student, Guardian
from .serializers import StudentSerializer, StudentCreateSerializer, GuardianSerializer
from apps.authentication.models import CustomUser
from apps.academics.models import Class, Section


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def student_list(request):
    if request.method == 'GET':
        school = request.user.school
        students = Student.objects.filter(school=school, is_active=True)
        # filters
        class_id = request.query_params.get('class_id')
        section_id = request.query_params.get('section_id')
        search = request.query_params.get('search')
        if class_id:
            students = students.filter(class_name_id=class_id)
        if section_id:
            students = students.filter(section_id=section_id)
        if search:
            students = students.filter(
                user__full_name__icontains=search
            ) | students.filter(student_id__icontains=search)
        serializer = StudentSerializer(students, many=True)
        return Response({'count': students.count(), 'results': serializer.data})

    if request.method == 'POST':
        serializer = StudentCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = CustomUser.objects.create_user(
                email=data['email'],
                full_name=data['full_name'],
                phone=data.get('phone', ''),
                password=data['password'],
                role='student',
                school=request.user.school
            )
            class_obj = None
            section_obj = None
            if data.get('class_name'):
                class_obj = Class.objects.filter(id=data['class_name']).first()
            if data.get('section'):
                section_obj = Section.objects.filter(id=data['section']).first()

            student = Student.objects.create(
                user=user,
                school=request.user.school,
                student_id=data['student_id'],
                class_name=class_obj,
                section=section_obj,
                dob=data.get('dob'),
                gender=data.get('gender', ''),
                blood_group=data.get('blood_group', ''),
                address=data.get('address', ''),
                religion=data.get('religion', ''),
            )
            return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk, school=request.user.school)

    if request.method == 'GET':
        return Response(StudentSerializer(student).data)

    if request.method == 'PATCH':
        data = request.data
        user = student.user
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'avatar' in data:
            user.avatar = data['avatar']
        user.save()
        if 'class_name' in data:
            student.class_name_id = data['class_name']
        if 'section' in data:
            student.section_id = data['section']
        if 'dob' in data:
            student.dob = data['dob']
        if 'gender' in data:
            student.gender = data['gender']
        if 'blood_group' in data:
            student.blood_group = data['blood_group']
        if 'address' in data:
            student.address = data['address']
        student.save()
        return Response(StudentSerializer(student).data)

    if request.method == 'DELETE':
        student.is_active = False
        student.save()
        return Response({'message': 'Student deactivated'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_guardian(request, pk):
    student = get_object_or_404(Student, pk=pk, school=request.user.school)
    serializer = GuardianSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(student=student)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)