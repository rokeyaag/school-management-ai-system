from django.db import models
from apps.tenants.models import School


class Class(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=50)
    numeric_value = models.IntegerField(default=1)

    class Meta:
        db_table = 'classes'
        unique_together = ['school', 'name']
        ordering = ['numeric_value']

    def __str__(self):
        return f'{self.name} - {self.school.name}'


class Section(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='sections')
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=10)
    capacity = models.IntegerField(default=40)
    class_teacher = models.ForeignKey(
        'teachers.Teacher', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='class_teacher_of'
    )

    class Meta:
        db_table = 'sections'
        unique_together = ['class_name', 'name']

    def __str__(self):
        return f'{self.class_name.name} - {self.name}'


class Subject(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='subjects')
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subjects')
    teacher = models.ForeignKey(
        'teachers.Teacher', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='subjects'
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    full_marks = models.IntegerField(default=100)
    pass_marks = models.IntegerField(default=33)

    class Meta:
        db_table = 'subjects'

    def __str__(self):
        return f'{self.name} ({self.class_name.name})'


class Timetable(models.Model):
    DAY_CHOICES = [
        ('saturday', 'Saturday'), ('sunday', 'Sunday'),
        ('monday', 'Monday'), ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'), ('thursday', 'Thursday'),
    ]

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='timetable')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
    day = models.CharField(max_length=15, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        db_table = 'timetable'

    def __str__(self):
        return f'{self.section} - {self.subject.name} - {self.day}'