from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils.text import slugify
from .models import School
from apps.authentication.models import CustomUser

@api_view(['POST'])
@permission_classes([AllowAny])
def register_school(request):
    school_name = request.data.get('school_name', '').strip()
    full_name = request.data.get('full_name', '').strip()
    email = request.data.get('email', '').strip()
    phone = request.data.get('phone', '').strip()
    password = request.data.get('password', '')
    if not all([school_name, full_name, email, password]):
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
    if CustomUser.objects.filter(email=email).exists():
        return Response({'email': ['This email is already registered.']}, status=status.HTTP_400_BAD_REQUEST)
    slug = slugify(school_name)
    base_slug = slug
    counter = 1
    while School.objects.filter(slug=slug).exists():
        slug = f'{base_slug}-{counter}'
        counter += 1
    school = School.objects.create(name=school_name, slug=slug, phone=phone, email=email, is_approved=False)
    user = CustomUser.objects.create_user(
        email=email, full_name=full_name, phone=phone,
        password=password, role='school_admin', school=school, is_staff=False,
    )
    return Response({'message': 'Registration submitted! Waiting for admin approval.'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def school_list(request):
    if request.user.role != 'super_admin':
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    schools = School.objects.all().order_by('-created_at')
    data = [{
        'id': str(s.id), 'name': s.name, 'email': s.email, 'phone': s.phone,
        'is_approved': s.is_approved, 'is_active': s.is_active, 'created_at': str(s.created_at),
        'plan': s.plan,
    } for s in schools]
    return Response(data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def approve_school(request, school_id):
    if request.user.role != 'super_admin':
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    try:
        school = School.objects.get(id=school_id)
        school.is_approved = request.data.get('is_approved', True)
        school.is_active = request.data.get('is_approved', True)
        school.save()
        return Response({'message': 'School updated', 'is_approved': school.is_approved})
    except School.DoesNotExist:
        return Response({'error': 'School not found'}, status=status.HTTP_404_NOT_FOUND)