from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from apps.authentication.models import CustomUser
import cloudinary.uploader

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_settings(request):
    user = request.user
    if request.method == 'GET':
        return Response({
            'full_name': user.full_name,
            'email': user.email,
            'phone': user.phone,
            'role': user.role,
            'avatar': user.avatar,
            'school': user.school.name if user.school else None,
        })
    # PUT
    user.full_name = request.data.get('full_name', user.full_name)
    user.phone = request.data.get('phone', user.phone)
    user.save()
    return Response({'message': 'Profile updated successfully'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    if not old_password or not new_password:
        return Response({'error': 'Both fields required'}, status=status.HTTP_400_BAD_REQUEST)
    if not user.check_password(old_password):
        return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
    if len(new_password) < 6:
        return Response({'error': 'Password must be at least 6 characters'}, status=status.HTTP_400_BAD_REQUEST)
    user.set_password(new_password)
    user.save()
    return Response({'message': 'Password changed successfully'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    user = request.user
    file = request.FILES.get('avatar')
    if not file:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    result = cloudinary.uploader.upload(file, folder='avatars', transformation=[{'width': 200, 'height': 200, 'crop': 'fill'}])
    user.avatar = result['secure_url']
    user.save()
    return Response({'avatar': user.avatar})

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def school_settings(request):
    user = request.user
    if user.role not in ['super_admin', 'school_admin']:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    school = user.school
    if not school:
        return Response({'error': 'No school found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response({
            'name': school.name,
            'address': school.address,
            'phone': school.phone,
            'email': school.email,
            'logo': school.logo,
            'website': school.website,
            'academic_year': school.academic_year,
            'plan': school.plan,
        })
    # PUT
    school.name = request.data.get('name', school.name)
    school.address = request.data.get('address', school.address)
    school.phone = request.data.get('phone', school.phone)
    school.email = request.data.get('email', school.email)
    school.website = request.data.get('website', school.website)
    school.academic_year = request.data.get('academic_year', school.academic_year)
    school.save()
    return Response({'message': 'School settings updated successfully'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_school_logo(request):
    user = request.user
    if user.role not in ['super_admin', 'school_admin']:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    file = request.FILES.get('logo')
    if not file:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    result = cloudinary.uploader.upload(file, folder='school_logos', transformation=[{'width': 300, 'height': 300, 'crop': 'fill'}])
    user.school.logo = result['secure_url']
    user.school.save()
    return Response({'logo': user.school.logo})