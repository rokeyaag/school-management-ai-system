from rest_framework import serializers
from .models import FeeCategory, FeeSchedule, FeePayment


class FeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCategory
        fields = ['id', 'name', 'description', 'is_active']
        read_only_fields = ['id']


class FeeScheduleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = FeeSchedule
        fields = ['id', 'category', 'category_name', 'amount', 'month', 'year', 'due_date', 'is_recurring']
        read_only_fields = ['id']


class FeePaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = FeePayment
        fields = ['id', 'student', 'student_name', 'student_id', 'category', 'category_name',
                  'amount', 'paid_amount', 'month', 'year', 'payment_method',
                  'transaction_id', 'status', 'paid_date', 'note', 'created_at']
        read_only_fields = ['id', 'created_at']


class FeeReportSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    total_amount = serializers.FloatField()
    paid_amount = serializers.FloatField()
    due_amount = serializers.FloatField()
    payments = FeePaymentSerializer(many=True)