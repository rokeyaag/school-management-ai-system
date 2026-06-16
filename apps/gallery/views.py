from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import GalleryAlbum, GalleryPhoto
from .serializers import GalleryAlbumSerializer, GalleryPhotoSerializer
import cloudinary.uploader
import cloudinary
import os

def get_school(user):
    if hasattr(user, 'school') and user.school:
        return user.school
    from apps.tenants.models import School
    return School.objects.first()

def is_admin(user):
    return user.role in ['school_admin', 'super_admin']

class GalleryAlbumViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = GalleryAlbumSerializer

    def get_queryset(self):
        school = get_school(self.request.user)
        if not school:
            return GalleryAlbum.objects.none()
        return GalleryAlbum.objects.filter(school=school).order_by('-created_at')

    def perform_create(self, serializer):
        if not is_admin(self.request.user):
            raise PermissionError("Only admin can create albums.")
        school = get_school(self.request.user)
        serializer.save(school=school)

    def destroy(self, request, *args, **kwargs):
        if not is_admin(request.user):
            return Response({'error': 'Permission denied'}, status=403)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='upload-photo')
    def upload_photo(self, request, pk=None):
        if not is_admin(request.user):
            return Response({'error': 'Permission denied'}, status=403)
        album = self.get_object()
        file = request.FILES.get('image')
        if not file:
            return Response({'error': 'No image provided'}, status=400)
        try:
            result = cloudinary.uploader.upload(
                file,
                folder="school_gallery",
                resource_type="image"
            )
            photo = GalleryPhoto.objects.create(
                album=album,
                image=result['public_id'],
                caption=request.data.get('caption', '')
            )
            return Response(GalleryPhotoSerializer(photo).data, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['delete'], url_path='photos/(?P<photo_id>[^/.]+)/delete')
    def delete_photo(self, request, photo_id=None):
        if not is_admin(request.user):
            return Response({'error': 'Permission denied'}, status=403)
        try:
            school = get_school(request.user)
            photo = GalleryPhoto.objects.get(id=photo_id, album__school=school)
            cloudinary.uploader.destroy(str(photo.image))
            photo.delete()
            return Response({'message': 'Deleted'}, status=204)
        except GalleryPhoto.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)