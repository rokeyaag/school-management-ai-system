from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GalleryAlbumViewSet

router = DefaultRouter()
router.register(r'albums', GalleryAlbumViewSet, basename='gallery')

urlpatterns = [path('', include(router.urls))]