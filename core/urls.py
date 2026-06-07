from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/tenants/', include('apps.tenants.urls')),
    path('api/students/', include('apps.students.urls')),
    path('api/teachers/', include('apps.teachers.urls')),
    path('api/academics/', include('apps.academics.urls')),
    path('api/attendance/', include('apps.attendance.urls')),
    path('api/exams/', include('apps.exams.urls')),
    path('api/assignments/', include('apps.assignments.urls')),
    path('api/fees/', include('apps.fees.urls')),
    path('api/notices/', include('apps.notices.urls')),
    path('api/leaves/', include('apps.leaves.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/subscriptions/', include('apps.subscriptions.urls')),
    path('api/ai/', include('apps.ai_engine.urls')),
]