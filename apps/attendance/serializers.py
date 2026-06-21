from rest_framework import serializers
from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_name', 'student_id', 'section', 'date', 'status', 'note', 'created_at']
        read_only_fields = ['id', 'created_at']


