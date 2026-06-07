from django.db import models
from apps.tenants.models import School
from apps.students.models import Student


class FeeCategory(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fee_categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'fee_categories'

    def __str__(self):
        return f'{self.name} - {self.school.name}'


class FeeSchedule(models.Model):
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'),
        (4, 'April'), (5, 'May'), (6, 'June'),
        (7, 'July'), (8, 'August'), (9, 'September'),
        (10, 'October'), (11, 'November'), (12, 'December'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fee_schedules')
    category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE, related_name='schedules')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.IntegerField(choices=MONTH_CHOICES, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    is_recurring = models.BooleanField(default=False)

    class Meta:
        db_table = 'fee_schedules'

    def __str__(self):
        return f'{self.category.name} - {self.amount}'


class FeePayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('bank', 'Bank Transfer'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('due', 'Due'),
        ('partial', 'Partial'),
        ('waived', 'Waived'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fee_payments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_payments')
    category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    month = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cash')
    transaction_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='due')
    paid_date = models.DateField(null=True, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fee_payments'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student} - {self.category.name} - {self.status}'