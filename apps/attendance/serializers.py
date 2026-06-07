from rest_framework import serializers
from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_name', 'student_id', 'section', 'date', 'status', 'note', 'created_at']
        read_only_fields = ['id', 'created_at']


class BulkAttendanceSerializer(serializers.Serializer):
    date = serializers.DateField()
    section_id = serializers.IntegerField()
    attendances = serializers.ListField(
        child=serializers.DictField()
    )

    def validate_attendances(self, value):
        for item in value:
            if 'student_id' not in item or 'status' not in item:
                raise serializers.ValidationError('Each item must have student_id and status')
            if item['status'] not in ['present', 'absent', 'late', 'excused']:
                raise serializers.ValidationError(f"Invalid status: {item['status']}")
        return value


class AttendanceReportSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    total_days = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    excused = serializers.IntegerField()
    percentage = serializers.FloatField()