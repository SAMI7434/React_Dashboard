from django.contrib import admin

from .models import ImportBatch, NormalizationLog, RawUtilityRecord, NormalizedUtilityRecord, ValidationIssue


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
	list_display = ('file_name', 'upload_time', 'uploaded_by', 'status')
	list_filter = ('status', 'upload_time')
	search_fields = ('file_name',)


@admin.register(RawUtilityRecord)
class RawUtilityRecordAdmin(admin.ModelAdmin):
	list_display = ('row_number', 'meter_id', 'facility_name', 'import_batch', 'ingested_at')
	list_filter = ('import_batch',)
	search_fields = ('meter_id', 'facility_name')


@admin.register(NormalizedUtilityRecord)
class NormalizedUtilityRecordAdmin(admin.ModelAdmin):
	list_display = ('meter_id', 'facility_name', 'billing_start', 'billing_end', 'total_cost', 'status', 'locked')
	list_filter = ('status', 'locked')
	search_fields = ('meter_id', 'facility_name')


@admin.register(ValidationIssue)
class ValidationIssueAdmin(admin.ModelAdmin):
	list_display = ('record', 'severity', 'message', 'created_at')
	list_filter = ('severity', 'created_at')


@admin.register(NormalizationLog)
class NormalizationLogAdmin(admin.ModelAdmin):
	list_display = ('record', 'original_value', 'original_unit', 'normalized_value', 'normalized_unit', 'review_status')
	list_filter = ('review_status', 'created_at')
