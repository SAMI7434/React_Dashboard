from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import ImportBatch, NormalizedUtilityRecord, NormalizationLog, RawUtilityRecord, ValidationIssue


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs.get('username'), password=attrs.get('password'))
        if not user:
            raise serializers.ValidationError('Invalid username or password.')
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class RawUtilityRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawUtilityRecord
        fields = (
            'id',
            'row_number',
            'meter_id',
            'facility_name',
            'billing_start_date',
            'billing_end_date',
            'usage_value',
            'usage_unit',
            'tariff_type',
            'total_cost',
            'cost_unit',
            'currency',
            'supplier_name',
            'raw_row',
            'ingested_at',
        )


class ValidationIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationIssue
        fields = ('id', 'severity', 'message', 'created_at')


class NormalizationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormalizationLog
        fields = (
            'id',
            'original_value',
            'original_unit',
            'normalized_value',
            'normalized_unit',
            'conversion_formula',
            'review_status',
            'created_at',
        )


class NormalizedUtilityRecordSerializer(serializers.ModelSerializer):
    issues = ValidationIssueSerializer(many=True, read_only=True)
    raw_record = RawUtilityRecordSerializer(read_only=True)
    normalization_logs = NormalizationLogSerializer(many=True, read_only=True)

    class Meta:
        model = NormalizedUtilityRecord
        fields = (
            'id',
            'import_batch',
            'raw_record',
            'meter_id',
            'facility_name',
            'billing_start',
            'billing_end',
            'usage_kwh',
            'original_energy_value',
            'original_energy_unit',
            'normalized_mwh',
            'tariff_type',
            'total_cost',
            'original_cost_value',
            'original_cost_unit',
            'normalized_thousand_dollars',
            'currency',
            'supplier_name',
            'status',
            'approved_by',
            'approved_at',
            'locked',
            'created_at',
            'issues',
            'normalization_logs',
        )


class ImportBatchSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.SerializerMethodField()
    record_count = serializers.SerializerMethodField()
    failed_count = serializers.SerializerMethodField()
    suspicious_count = serializers.SerializerMethodField()
    approved_count = serializers.SerializerMethodField()

    class Meta:
        model = ImportBatch
        fields = (
            'id',
            'file_name',
            'upload_time',
            'uploaded_by',
            'status',
            'record_count',
            'failed_count',
            'suspicious_count',
            'approved_count',
        )

    def get_uploaded_by(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.username
        return None

    def get_record_count(self, obj):
        return obj.normalized_records.count()

    def get_failed_count(self, obj):
        return obj.normalized_records.filter(issues__severity='error').distinct().count()

    def get_suspicious_count(self, obj):
        return obj.normalized_records.filter(issues__severity='warning').distinct().count()

    def get_approved_count(self, obj):
        return obj.normalized_records.filter(status='approved').count()


class UploadFileSerializer(serializers.Serializer):
    file = serializers.FileField()
