from rest_framework import serializers
from .models import Exam, Marks


class ExamSerializer(serializers.ModelSerializer):
    class_name_display = serializers.CharField(source='class_name.name', read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'name', 'exam_type', 'class_name', 'class_name_display',
                  'start_date', 'end_date', 'is_published', 'created_at']
        read_only_fields = ['id', 'created_at']


class MarksSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = Marks
        fields = ['id', 'exam', 'student', 'student_name', 'subject', 'subject_name',
                  'marks_obtained', 'total_marks', 'grade', 'grade_point',
                  'is_absent', 'created_at']
        read_only_fields = ['id', 'grade', 'grade_point', 'created_at']


class BulkMarksSerializer(serializers.Serializer):
    exam_id = serializers.IntegerField()
    marks = serializers.ListField(child=serializers.DictField())

    def validate_marks(self, value):
        for item in value:
            if 'student_id' not in item or 'subject_id' not in item:
                raise serializers.ValidationError('student_id and subject_id required')
        return value


class ResultCardSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    student_roll = serializers.CharField()
    exam_name = serializers.CharField()
    subjects = serializers.ListField()
    total_marks = serializers.FloatField()
    obtained_marks = serializers.FloatField()
    gpa = serializers.FloatField()
    result = serializers.CharField()
    position = serializers.IntegerField()