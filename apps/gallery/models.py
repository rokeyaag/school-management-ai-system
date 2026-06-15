from django.db import models
from apps.tenants.models import School
import cloudinary.models

class GalleryAlbum(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='albums')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.school.name} - {self.title}"

class GalleryPhoto(models.Model):
    album = models.ForeignKey(GalleryAlbum, on_delete=models.CASCADE, related_name='photos')
    image = cloudinary.models.CloudinaryField('image')
    caption = models.CharField(max_length=300, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.album.title} - {self.uploaded_at}"