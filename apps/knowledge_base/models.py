from django.db import models
from apps.tenants.models import School
from apps.authentication.models import CustomUser

class Subject(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='kb_subjects')
    name = models.CharField(max_length=100)
    name_bn = models.CharField(max_length=100, blank=True)
    class_name = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'kb_subjects'

    def __str__(self):
        return f'{self.name} ({self.class_name})'

class Document(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    ]
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='kb_documents')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    file = models.URLField(blank=True)
    raw_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    chunk_count = models.IntegerField(default=0)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'kb_documents'
        ordering = ['-created_at']

    def __str__(self):
        return self.title