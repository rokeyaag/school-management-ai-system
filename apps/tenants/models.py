from django.db import models
import uuid


class School(models.Model):
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('ai', 'AI'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    logo = models.URLField(blank=True)
    website = models.URLField(blank=True)
    academic_year = models.CharField(max_length=10, default='2025-26')
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='basic')
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'schools'
        verbose_name = 'School'

    def __str__(self):
        return self.name