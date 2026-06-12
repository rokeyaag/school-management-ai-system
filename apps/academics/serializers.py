from rest_framework import serializers
from apps.academics.models import Class, Section, Subject, Timetable

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'name', 'numeric_value']

class SectionSerializer(serializers.ModelSerializer):
    class_name_display = serializers.CharField(source='class_name.name', read_only=True)
    class Meta:
        model = Section
        fields = ['id', 'name', 'capacity', 'class_name', 'class_name_display']

class SubjectSerializer(serializers.ModelSerializer):
    class_name_display = serializers.CharField(source='class_name.name', read_only=True)
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'full_marks', 'pass_marks', 'class_name', 'class_name_display']

class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = ['id', 'section', 'subject', 'teacher', 'day', 'start_time', 'end_time']