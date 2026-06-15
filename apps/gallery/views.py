from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import GalleryAlbum, GalleryPhoto
from .serializers import GalleryAlbumSerializer, GalleryPhotoSerializer
import cloudinary.uploader

class GalleryAlbumViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = GalleryAlbumSerializer

    def get_queryset(self):
        school = self.request.user.school
        return GalleryAlbum.objects.filter(school=school).order_by('-created_at')

    def perform_create(self, serializer):
        if self.request.user.role != 'school_admin':
            raise PermissionError("Only school_admin can create albums.")
        serializer.save(school=self.request.user.school)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'school_admin':
            return Response({'error': 'Permission denied'}, status=403)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='upload-photo')
    def upload_photo(self, request, pk=None):
        if request.user.role != 'school_admin':
            return Response({'error': 'Permission denied'}, status=403)
        album = self.get_object()
        file = request.FILES.get('image')
        if not file:
            return Response({'error': 'No image provided'}, status=400)
        result = cloudinary.uploader.upload(file, upload_preset='dv1zh1rc')
        photo = GalleryPhoto.objects.create(
            album=album,
            image=result['public_id'],
            caption=request.data.get('caption', '')
        )
        return Response(GalleryPhotoSerializer(photo).data, status=201)

    @action(detail=False, methods=['delete'], url_path='photos/(?P<photo_id>[^/.]+)/delete')
    def delete_photo(self, request, photo_id=None):
        if request.user.role != 'school_admin':
            return Response({'error': 'Permission denied'}, status=403)
        try:
            photo = GalleryPhoto.objects.get(id=photo_id, album__school=request.user.school)
            cloudinary.uploader.destroy(str(photo.image))
            photo.delete()
            return Response({'message': 'Deleted'}, status=204)
        except GalleryPhoto.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)