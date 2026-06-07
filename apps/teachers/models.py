from django.db import models
from apps.tenants.models import School
from apps.authentication.models import CustomUser


class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='teachers')
    employee_id = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    join_date = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'teachers'
        ordering = ['employee_id']

    def __str__(self):
        return f'{self.user.full_name} ({self.employee_id})'