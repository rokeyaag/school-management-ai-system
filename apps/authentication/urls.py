from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import settings_views
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change-password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('settings/profile/', settings_views.profile_settings, name='profile-settings'),
    path('settings/change-password/', settings_views.change_password, name='settings-change-password'),
    path('settings/avatar/', settings_views.upload_avatar, name='upload-avatar'),
    path('settings/school/', settings_views.school_settings, name='school-settings'),
    path('settings/school-logo/', settings_views.upload_school_logo, name='upload-school-logo'),
]