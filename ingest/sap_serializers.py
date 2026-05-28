from rest_framework import serializers
from .models import (
    SAPImportBatch,
    RawSAPRecord,
    NormalizedSAPRecord,
    SAPValidationIssue,
    SAPApprovalLog,
)


class SAPImportBatchSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)

    class Meta:
        model = SAPImportBatch
        fields = '__all__'


class RawSAPRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawSAPRecord
        fields = '__all__'


class SAPValidationIssueSerializer(serializers.ModelSerializer):
    record_id = serializers.IntegerField(source='record.id', read_only=True)
    record_material = serializers.CharField(source='record.material_number', read_only=True)
    record_plant = serializers.CharField(source='record.plant_code', read_only=True)

    class Meta:
        model = SAPValidationIssue
        fields = '__all__'


class SAPApprovalLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    record_id = serializers.IntegerField(source='record.id', read_only=True)
    record_material = serializers.CharField(source='record.material_number', read_only=True)

    class Meta:
        model = SAPApprovalLog
        fields = '__all__'


class NormalizedSAPRecordSerializer(serializers.ModelSerializer):
    issues_count = serializers.SerializerMethodField()
    has_issues = serializers.SerializerMethodField()
    approval_logs_count = serializers.SerializerMethodField()

    class Meta:
        model = NormalizedSAPRecord
        fields = '__all__'

    def get_issues_count(self, obj):
        return obj.sap_issues.count()

    def get_has_issues(self, obj):
        return obj.sap_issues.exists()

    def get_approval_logs_count(self, obj):
        return obj.approval_logs.count()


class NormalizedSAPRecordDetailSerializer(serializers.ModelSerializer):
    sap_issues = SAPValidationIssueSerializer(many=True, read_only=True)
    approval_logs = SAPApprovalLogSerializer(many=True, read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True)

    class Meta:
        model = NormalizedSAPRecord
        fields = '__all__'