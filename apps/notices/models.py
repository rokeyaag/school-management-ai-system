from django.db import models
from apps.tenants.models import School
from apps.authentication.models import CustomUser

class Notice(models.Model):
    TARGET_CHOICES = [
        ('all', 'All'),
        ('student', 'Students'),
        ('teacher', 'Teachers'),
        ('parent', 'Parents'),
        ('admin', 'Admin'),
    ]
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='notices')
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='notices')
    title = models.CharField(max_length=200)
    content = models.TextField()
    target_role = models.CharField(max_length=10, choices=TARGET_CHOICES, default='all')
    attachment = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    read_by = models.ManyToManyField(CustomUser, blank=True, related_name='read_notices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notices'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.school.name}'