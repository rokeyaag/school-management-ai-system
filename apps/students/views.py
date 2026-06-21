from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from .models import Student, Guardian
from .serializers import StudentSerializer, StudentCreateSerializer, GuardianSerializer
from apps.authentication.models import CustomUser
from apps.academics.models import Class, Section


def generate_student_id(school):
    last = Student.objects.filter(school=school).order_by('-created_at').first()
    if last and last.student_id.startswith('STU-'):
        try:
            num = int(last.student_id.split('-')[1]) + 1
        except:
            num = 1
    else:
        num = 1
    return f'STU-{num:04d}'


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def student_list(request):
    if request.method == 'GET':
        school = request.user.school
        if request.user.role == 'student':
            try:
                student = Student.objects.get(user=request.user, school=school)
                return Response({'count': 1, 'results': [StudentSerializer(student).data]})
            except Student.DoesNotExist:
                return Response({'count': 0, 'results': []})
        students = Student.objects.filter(school=school, is_active=True)
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
            school = request.user.school
            try:
                user = CustomUser.objects.create_user(
                    email=data['email'],
                    full_name=data['full_name'],
                    phone=data.get('phone', ''),
                    password=data['password'],
                    role='student',
                    school=school
                )
            except IntegrityError:
                return Response({'email': ['This email is already registered.']}, status=status.HTTP_400_BAD_REQUEST)
            class_obj = None
            section_obj = None
            if data.get('class_name'):
                class_obj = Class.objects.filter(id=data['class_name']).first()
            if data.get('section'):
                section_obj = Section.objects.filter(id=data['section']).first()

            student_id = data.get('student_id') or generate_student_id(school)

            student = Student.objects.create(
                user=user, school=school,
                student_id=student_id,
                roll=data.get('roll', ''),
                class_name=class_obj, section=section_obj,
                name_bangla=data.get('name_bangla', ''),
                dob=data.get('dob'),
                birth_reg_no=data.get('birth_reg_no', ''),
                gender=data.get('gender', ''),
                blood_group=data.get('blood_group', ''),
                religion=data.get('religion', ''),
                photo=data.get('photo', ''),
                present_address=data.get('present_address', ''),
                permanent_address=data.get('permanent_address', ''),
                father_name=data.get('father_name', ''),
                father_nid=data.get('father_nid', ''),
                father_mobile=data.get('father_mobile', ''),
                mother_name=data.get('mother_name', ''),
                mother_nid=data.get('mother_nid', ''),
                mother_mobile=data.get('mother_mobile', ''),
                guardian_name=data.get('guardian_name', ''),
                guardian_mobile=data.get('guardian_mobile', ''),
                guardian_relation=data.get('guardian_relation', ''),
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
        for field in ['full_name', 'phone', 'avatar']:
            if field in data:
                setattr(user, field, data[field])
        user.save()
        for field in ['roll', 'name_bangla', 'dob', 'birth_reg_no', 'gender',
                      'blood_group', 'religion', 'photo', 'present_address',
                      'permanent_address', 'father_name', 'father_nid', 'father_mobile',
                      'mother_name', 'mother_nid', 'mother_mobile',
                      'guardian_name', 'guardian_mobile', 'guardian_relation',
                      'class_name_id', 'section_id']:
            if field in data:
                setattr(student, field, data[field])
        student.save()
        return Response(StudentSerializer(student).data)
    student.is_active = False
    student.save()
    return Response({'message': 'Student deactivated'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_id(request):
    school = request.user.school
    new_id = generate_student_id(school)
    return Response({'student_id': new_id})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_guardian(request, pk):
    student = get_object_or_404(Student, pk=pk, school=request.user.school)
    serializer = GuardianSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(student=student)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)