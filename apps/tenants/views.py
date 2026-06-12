from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
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

    school = School.objects.create(name=school_name, slug=slug, phone=phone, email=email)

    user = CustomUser.objects.create_user(
        email=email,
        full_name=full_name,
        phone=phone,
        password=password,
        role='school_admin',
        school=school,
        is_staff=False,
    )

    return Response({'message': 'School registered successfully!', 'school': school_name}, status=status.HTTP_201_CREATED)