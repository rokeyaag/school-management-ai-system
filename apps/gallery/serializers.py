from rest_framework import serializers
from .models import GalleryAlbum, GalleryPhoto

class GalleryPhotoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = GalleryPhoto
        fields = ['id', 'image_url', 'caption', 'uploaded_at']

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None

class GalleryAlbumSerializer(serializers.ModelSerializer):
    photos = GalleryPhotoSerializer(many=True, read_only=True)
    photo_count = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = GalleryAlbum
        fields = ['id', 'title', 'description', 'created_at', 'photo_count', 'cover_image', 'photos']

    def get_photo_count(self, obj):
        return obj.photos.count()

    def get_cover_image(self, obj):
        first = obj.photos.first()
        return first.image.url if first else None