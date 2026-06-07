from django.db import models
from apps.tenants.models import School
from apps.students.models import Student
from apps.academics.models import Class, Subject


class Exam(models.Model):
    EXAM_TYPE_CHOICES = [
        ('ct1', 'Class Test 1'),
        ('ct2', 'Class Test 2'),
        ('half_yearly', 'Half Yearly'),
        ('annual', 'Annual'),
        ('mock', 'Mock Test'),
        ('other', 'Other'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exams')
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='exams')
    name = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES, default='other')
    start_date = models.DateField()
    end_date = models.DateField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'exams'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.name} - {self.class_name.name}'


class Marks(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='marks')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='marks')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    grade = models.CharField(max_length=5, blank=True)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    is_absent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'marks'
        unique_together = ['exam', 'student', 'subject']

    def __str__(self):
        return f'{self.student} - {self.subject.name} - {self.marks_obtained}'

    def save(self, *args, **kwargs):
        self.grade, self.grade_point = self.calculate_grade()
        super().save(*args, **kwargs)

    def calculate_grade(self):
        if self.is_absent:
            return 'F', 0.00
        percentage = (float(self.marks_obtained) / float(self.total_marks)) * 100
        if percentage >= 80:
            return 'A+', 5.00
        elif percentage >= 70:
            return 'A', 4.00
        elif percentage >= 60:
            return 'A-', 3.50
        elif percentage >= 50:
            return 'B', 3.00
        elif percentage >= 40:
            return 'C', 2.00
        elif percentage >= 33:
            return 'D', 1.00
        else:
            return 'F', 0.00