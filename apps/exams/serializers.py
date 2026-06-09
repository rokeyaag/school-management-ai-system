from rest_framework import serializers
from .models import Exam, Marks
from apps.academics.models import Class, Subject


class ExamSerializer(serializers.ModelSerializer):
    class_name_display = serializers.CharField(source='class_name.name', read_only=True)
    exam_type_display = serializers.CharField(source='get_exam_type_display', read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'name', 'exam_type', 'exam_type_display', 'class_name',
                  'class_name_display', 'start_date', 'end_date', 'is_published', 'created_at']
        read_only_fields = ['id', 'created_at']


class MarksSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    photo = serializers.CharField(source='student.photo', read_only=True)

    class Meta:
        model = Marks
        fields = ['id', 'exam', 'student', 'student_name', 'student_id', 'photo',
                  'subject', 'subject_name', 'marks_obtained', 'total_marks',
                  'grade', 'grade_point', 'is_absent', 'created_at']
        read_only_fields = ['id', 'grade', 'grade_point', 'created_at']