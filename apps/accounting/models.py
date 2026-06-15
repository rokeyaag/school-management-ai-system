from django.db import models
from apps.tenants.models import School
from apps.authentication.models import CustomUser

class ExpenseCategory(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='expense_categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'expense_categories'
    def __str__(self):
        return self.name

class Expense(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, related_name='expenses')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    payment_method = models.CharField(max_length=50, choices=[('cash','Cash'),('bank','Bank Transfer'),('bkash','bKash'),('nagad','Nagad')], default='cash')
    note = models.TextField(blank=True)
    added_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'expenses'
        ordering = ['-date']
    def __str__(self):
        return f'{self.title} - {self.amount}'

class Income(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='incomes')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    source = models.CharField(max_length=100, choices=[('fee','Student Fee'),('donation','Donation'),('government','Government Grant'),('other','Other')], default='other')
    note = models.TextField(blank=True)
    added_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'incomes'
        ordering = ['-date']
    def __str__(self):
        return f'{self.title} - {self.amount}'

class SalaryPayment(models.Model):
    STATUS_CHOICES = [('paid','Paid'),('pending','Pending'),('partial','Partial')]
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='salary_payments')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, related_name='salary_payments')
    month = models.IntegerField()
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, choices=[('cash','Cash'),('bank','Bank Transfer'),('bkash','bKash'),('nagad','Nagad')], default='cash')
    payment_date = models.DateField(null=True, blank=True)
    note = models.TextField(blank=True)
    paid_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'salary_payments'
        ordering = ['-year', '-month']
    def __str__(self):
        return f'{self.teacher.user.full_name} - {self.month}/{self.year}'