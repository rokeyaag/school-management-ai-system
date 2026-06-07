from django.db import models
from apps.tenants.models import School
from apps.authentication.models import CustomUser


class Student(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'), ('female', 'Female'), ('other', 'Other'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    student_id = models.CharField(max_length=20, unique=True)
    class_name = models.ForeignKey('academics.Class', on_delete=models.SET_NULL, null=True, related_name='students')
    section = models.ForeignKey('academics.Section', on_delete=models.SET_NULL, null=True, related_name='students')
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    address = models.TextField(blank=True)
    religion = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'students'
        ordering = ['student_id']

    def __str__(self):
        return f'{self.user.full_name} ({self.student_id})'


class Guardian(models.Model):
    RELATION_CHOICES = [
        ('father', 'Father'), ('mother', 'Mother'),
        ('guardian', 'Guardian'), ('other', 'Other'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='guardians')
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES)
    occupation = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'guardians'

    def __str__(self):
        return f'{self.name} ({self.relation} of {self.student})'