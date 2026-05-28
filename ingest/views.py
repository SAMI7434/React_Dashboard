import csv
from io import TextIOWrapper
from decimal import Decimal
import logging

from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import ImportBatch, NormalizedUtilityRecord, NormalizationLog, RawUtilityRecord, ValidationIssue
from .serializers import (
	ImportBatchSerializer,
	LoginSerializer,
	NormalizedUtilityRecordSerializer,
	UploadFileSerializer,
	UserSerializer,
	ValidationIssueSerializer,
)
from .services import (
	clean_string,
	normalize_cost_to_thousand,
	normalize_energy_to_mwh,
	normalize_usage_kwh,
	parse_date,
	parse_decimal,
)

logger = logging.getLogger(__name__)


COLUMN_ALIASES = {
	'meter_id': ['meter_id', 'meter id', 'meter number', 'meter_number'],
	'facility_name': ['facility_name', 'facility', 'site', 'location'],
	'billing_start_date': ['billing_start_date', 'billing_start', 'start_date', 'bill_start', 'billing period start'],
	'billing_end_date': ['billing_end_date', 'billing_end', 'end_date', 'bill_end', 'billing period end'],
	'usage_value': ['usage_value', 'usage', 'consumption', 'kwh', 'usage_value_kwh'],
	'usage_unit': ['usage_unit', 'unit', 'uom', 'usage_uom'],
	'tariff_type': ['tariff_type', 'tariff', 'rate_plan', 'rate plan'],
	'total_cost': ['total_cost', 'amount', 'total', 'bill_amount', 'cost'],
	'cost_unit': ['cost_unit', 'cost unit', 'cost_uom', 'amount_unit', 'financial_unit'],
	'currency': ['currency', 'currency_code', 'ccy'],
	'supplier_name': ['supplier_name', 'supplier', 'utility', 'provider'],
}


def get_column_value(row, field_name):
	for alias in COLUMN_ALIASES.get(field_name, []):
		for key in row.keys():
			if key.strip().lower() == alias:
				return row.get(key)
	return None


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
	serializer = LoginSerializer(data=request.data)
	serializer.is_valid(raise_exception=True)
	user = serializer.validated_data['user']
	token, _ = Token.objects.get_or_create(user=user)
	return Response({'token': token.key, 'user': UserSerializer(user).data})


@api_view(['GET'])
def me_view(request):
	return Response(UserSerializer(request.user).data)


@api_view(['POST'])
def upload_csv_view(request):
	serializer = UploadFileSerializer(data=request.data)
	serializer.is_valid(raise_exception=True)
	upload_file = serializer.validated_data['file']
	batch = ImportBatch.objects.create(
		file_name=upload_file.name,
		uploaded_by=request.user,
		status='processing',
	)

	created_records = 0
	error_rows = 0
	warning_rows = 0
	energy_spike_threshold_mwh = Decimal('200000')
	cost_spike_threshold_thousand = Decimal('5000')

	try:
		text_stream = TextIOWrapper(upload_file.file, encoding='utf-8-sig')
		reader = csv.DictReader(text_stream)

		# Pre-fetch existing records for spike detection (batch optimization)
		existing_records_by_meter = {}
		existing_records = (
			NormalizedUtilityRecord.objects
			.filter(normalized_mwh__isnull=False)
			.values('meter_id', 'billing_end', 'normalized_mwh')
			.order_by('meter_id', '-billing_end')
		)
		for rec in existing_records:
			mid = rec['meter_id']
			if mid not in existing_records_by_meter:
				existing_records_by_meter[mid] = rec

		# Batch create lists
		raw_records_to_create = []
		normalized_records_to_create = []
		normalization_logs_to_create = []
		validation_issues_to_create = []

		for index, row in enumerate(reader, start=1):
			meter_id = clean_string(get_column_value(row, 'meter_id'))
			facility_name = clean_string(get_column_value(row, 'facility_name'))
			billing_start_raw = clean_string(get_column_value(row, 'billing_start_date'))
			billing_end_raw = clean_string(get_column_value(row, 'billing_end_date'))
			usage_value_raw = get_column_value(row, 'usage_value')
			usage_unit = clean_string(get_column_value(row, 'usage_unit'))
			tariff_type = clean_string(get_column_value(row, 'tariff_type'))
			total_cost_raw = get_column_value(row, 'total_cost')
			cost_unit = clean_string(get_column_value(row, 'cost_unit'))
			currency = clean_string(get_column_value(row, 'currency'))
			supplier_name = clean_string(get_column_value(row, 'supplier_name'))

			# Parse values
			billing_start = parse_date(billing_start_raw)
			billing_end = parse_date(billing_end_raw)
			energy_value = parse_decimal(usage_value_raw)
			cost_value = parse_decimal(total_cost_raw)
			normalized_mwh, energy_unit_label, energy_formula = normalize_energy_to_mwh(energy_value, usage_unit)
			normalized_thousand, cost_unit_label, cost_formula = normalize_cost_to_thousand(cost_value, cost_unit)
			usage_kwh = None
			if normalized_mwh is not None:
				usage_kwh = normalized_mwh * Decimal('1000')

			# Validation
			issues = []
			if not meter_id:
				issues.append(('error', 'Missing meter_id.'))
			if billing_start is None:
				issues.append(('error', 'Invalid or missing billing_start_date.'))
			if billing_end is None:
				issues.append(('error', 'Invalid or missing billing_end_date.'))
			if billing_start and billing_end and billing_end < billing_start:
				issues.append(('error', 'billing_end_date occurs before billing_start_date.'))
			if energy_value is None:
				issues.append(('error', 'Missing usage_value.'))
			if usage_unit == '':
				issues.append(('error', 'Missing energy unit.'))
			elif normalized_mwh is None:
				issues.append(('error', 'Unknown energy unit.'))
			if normalized_mwh is not None and normalized_mwh > energy_spike_threshold_mwh:
				issues.append(('warning', 'Extremely high energy after normalization.'))
			if usage_unit.strip().lower() in ['dollars', 'thousand dollars', 'million dollars']:
				issues.append(('error', 'Energy unit appears to be a financial unit.'))
			if cost_value is None:
				issues.append(('error', 'Missing total_cost.'))
			if cost_unit == '':
				issues.append(('error', 'Missing cost unit.'))
			elif normalized_thousand is None:
				issues.append(('error', 'Unknown cost unit.'))
			if normalized_thousand is not None and normalized_thousand > cost_spike_threshold_thousand:
				issues.append(('warning', 'Extremely high cost after normalization.'))
			if cost_unit.strip().lower() in ['wh', 'kwh', 'mwh', 'gwh', 'btu']:
				issues.append(('error', 'Cost unit appears to be an energy unit.'))
			if cost_value is not None and cost_value < Decimal('0'):
				issues.append(('warning', 'Negative total_cost.'))
			if not currency:
				issues.append(('warning', 'Missing currency.'))
			if not supplier_name:
				issues.append(('warning', 'Missing supplier_name.'))

			# Spike detection using pre-fetched data (no DB query per row)
			previous = existing_records_by_meter.get(meter_id)
			if previous and normalized_mwh is not None and previous['normalized_mwh']:
				if normalized_mwh > (previous['normalized_mwh'] * Decimal('3')):
					issues.append(('warning', 'Usage spike greater than 3x previous cycle.'))

			has_errors = any(severity == 'error' for severity, _ in issues)
			has_warnings = any(severity == 'warning' for severity, _ in issues)

			if has_errors:
				error_rows += 1
			if has_warnings:
				warning_rows += 1
			created_records += 1

			# Prepare raw record
			raw_records_to_create.append(RawUtilityRecord(
				import_batch=batch,
				row_number=index,
				meter_id=meter_id,
				facility_name=facility_name,
				billing_start_date=billing_start_raw,
				billing_end_date=billing_end_raw,
				usage_value=parse_decimal(usage_value_raw),
				usage_unit=usage_unit,
				tariff_type=tariff_type,
				total_cost=parse_decimal(total_cost_raw),
				cost_unit=cost_unit,
				currency=currency,
				supplier_name=supplier_name,
				raw_row=row,
			))

		# Bulk create raw records first
		if raw_records_to_create:
			created_raw = RawUtilityRecord.objects.bulk_create(raw_records_to_create, batch_size=100)
			# Map created records by row_number for easy lookup
			raw_record_map = {r.row_number: r for r in created_raw}

			# Process normalized records
			for i, raw in enumerate(raw_records_to_create):
				row = raw.raw_row
				meter_id = raw.meter_id
				facility_name = raw.facility_name
				billing_start_raw = raw.billing_start_date
				billing_end_raw = raw.billing_end_date
				usage_value_raw = raw.usage_value
				usage_unit = raw.usage_unit
				tariff_type = raw.tariff_type
				total_cost_raw = raw.total_cost
				cost_unit = raw.cost_unit
				currency = raw.currency
				supplier_name = raw.supplier_name

				billing_start = parse_date(billing_start_raw)
				billing_end = parse_date(billing_end_raw)
				energy_value = parse_decimal(usage_value_raw)
				cost_value = parse_decimal(total_cost_raw)
				normalized_mwh, energy_unit_label, energy_formula = normalize_energy_to_mwh(energy_value, usage_unit)
				normalized_thousand, cost_unit_label, cost_formula = normalize_cost_to_thousand(cost_value, cost_unit)
				usage_kwh = None
				if normalized_mwh is not None:
					usage_kwh = normalized_mwh * Decimal('1000')

				normalized_records_to_create.append(NormalizedUtilityRecord(
					import_batch=batch,
					raw_record=created_raw[i],
					meter_id=meter_id or 'UNKNOWN',
					facility_name=facility_name or 'Unknown Facility',
					billing_start=billing_start,
					billing_end=billing_end,
					usage_kwh=usage_kwh,
					original_energy_value=energy_value,
					original_energy_unit=usage_unit,
					normalized_mwh=normalized_mwh,
					tariff_type=tariff_type,
					total_cost=cost_value,
					original_cost_value=cost_value,
					original_cost_unit=cost_unit,
					normalized_thousand_dollars=normalized_thousand,
					currency=currency,
					supplier_name=supplier_name,
				))

				# Prepare normalization logs
				if energy_value is not None or usage_unit:
					normalization_logs_to_create.append(NormalizationLog(
						record=normalized_records_to_create[-1],
						original_value=energy_value,
						original_unit=usage_unit,
						normalized_value=normalized_mwh,
						normalized_unit=energy_unit_label or '',
						conversion_formula=energy_formula,
					))

				if cost_value is not None or cost_unit:
					normalization_logs_to_create.append(NormalizationLog(
						record=normalized_records_to_create[-1],
						original_value=cost_value,
						original_unit=cost_unit,
						normalized_value=normalized_thousand,
						normalized_unit=cost_unit_label or '',
						conversion_formula=cost_formula,
					))

			# Bulk create normalized records
			if normalized_records_to_create:
				created_normalized = NormalizedUtilityRecord.objects.bulk_create(normalized_records_to_create, batch_size=100)

				# Now create validation issues and update normalization logs with correct record references
				# Re-process for validation issues (need the created records)
				for i, normalized in enumerate(created_normalized):
					raw = normalized.raw_record
					# Re-calculate issues for this record
					issues = []
					if not raw.meter_id:
						issues.append(('error', 'Missing meter_id.'))
					if not raw.billing_start_date or parse_date(raw.billing_start_date) is None:
						issues.append(('error', 'Invalid or missing billing_start_date.'))
					if not raw.billing_end_date or parse_date(raw.billing_end_date) is None:
						issues.append(('error', 'Invalid or missing billing_end_date.'))
					billing_start = parse_date(raw.billing_start_date)
					billing_end = parse_date(raw.billing_end_date)
					if billing_start and billing_end and billing_end < billing_start:
						issues.append(('error', 'billing_end_date occurs before billing_start_date.'))
					if raw.usage_value is None:
						issues.append(('error', 'Missing usage_value.'))
					if raw.usage_unit == '':
						issues.append(('error', 'Missing energy unit.'))
					elif normalize_energy_to_mwh(raw.usage_value, raw.usage_unit)[0] is None:
						issues.append(('error', 'Unknown energy unit.'))
					normalized_mwh = normalized.normalized_mwh
					if normalized_mwh is not None and normalized_mwh > energy_spike_threshold_mwh:
						issues.append(('warning', 'Extremely high energy after normalization.'))
					if raw.usage_unit and raw.usage_unit.strip().lower() in ['dollars', 'thousand dollars', 'million dollars']:
						issues.append(('error', 'Energy unit appears to be a financial unit.'))
					if raw.total_cost is None:
						issues.append(('error', 'Missing total_cost.'))
					if raw.cost_unit == '':
						issues.append(('error', 'Missing cost unit.'))
					elif normalize_cost_to_thousand(raw.total_cost, raw.cost_unit)[0] is None:
						issues.append(('error', 'Unknown cost unit.'))
					normalized_thousand = normalized.normalized_thousand_dollars
					if normalized_thousand is not None and normalized_thousand > cost_spike_threshold_thousand:
						issues.append(('warning', 'Extremely high cost after normalization.'))
					if raw.cost_unit and raw.cost_unit.strip().lower() in ['wh', 'kwh', 'mwh', 'gwh', 'btu']:
						issues.append(('error', 'Cost unit appears to be an energy unit.'))
					if raw.total_cost is not None and raw.total_cost < Decimal('0'):
						issues.append(('warning', 'Negative total_cost.'))
					if not raw.currency:
						issues.append(('warning', 'Missing currency.'))
					if not raw.supplier_name:
						issues.append(('warning', 'Missing supplier_name.'))

					previous = existing_records_by_meter.get(raw.meter_id)
					if previous and normalized_mwh is not None and previous['normalized_mwh']:
						if normalized_mwh > (previous['normalized_mwh'] * Decimal('3')):
							issues.append(('warning', 'Usage spike greater than 3x previous cycle.'))

					for severity, message in issues:
						validation_issues_to_create.append(ValidationIssue(
							record=normalized,
							severity=severity,
							message=message,
						))

				# Bulk create validation issues
				if validation_issues_to_create:
					ValidationIssue.objects.bulk_create(validation_issues_to_create, batch_size=100)

				# Bulk create normalization logs (need to update record references)
				# Since bulk_create doesn't return IDs for SQLite, we need to handle this differently
				# For now, create logs individually but in a transaction
				with transaction.atomic():
					for log in normalization_logs_to_create:
						log.save()

		batch.status = 'completed'
		batch.save(update_fields=['status'])
	except Exception as e:
		logger.error(f"Upload failed for batch {batch.id}: {str(e)}")
		batch.status = 'failed'
		batch.save(update_fields=['status'])
		raise

	failed_rows = (
		NormalizedUtilityRecord.objects.filter(import_batch=batch, issues__severity='error')
		.distinct()
		.select_related('raw_record')
		.prefetch_related('issues')
	)
	suspicious_rows = (
		NormalizedUtilityRecord.objects.filter(import_batch=batch, issues__severity='warning')
		.distinct()
		.select_related('raw_record')
		.prefetch_related('issues')
	)

	return Response(
		{
			'batch': ImportBatchSerializer(batch).data,
			'records_created': created_records,
			'failed_records': error_rows,
			'suspicious_records': warning_rows,
			'failed_rows': NormalizedUtilityRecordSerializer(failed_rows, many=True).data,
			'suspicious_rows': NormalizedUtilityRecordSerializer(suspicious_rows, many=True).data,
		},
		status=status.HTTP_201_CREATED,
	)


@api_view(['GET'])
def dashboard_view(request):
	records = NormalizedUtilityRecord.objects.all()
	total_records = records.count()
	total_thousand = records.filter(status__in=['pending', 'approved']).aggregate(sum=Sum('normalized_thousand_dollars'))['sum'] or Decimal('0')
	total_mwh = records.filter(status__in=['pending', 'approved']).aggregate(sum=Sum('normalized_mwh'))['sum'] or Decimal('0')

	failed_count = records.filter(issues__severity='error').distinct().count()
	suspicious_count = records.filter(issues__severity='warning').distinct().count()

	monthly_cost = {}
	monthly_usage = {}
	tariff_breakdown = {}

	for record in records.exclude(billing_end__isnull=True):
		month_key = record.billing_end.strftime('%Y-%m')
		monthly_cost[month_key] = monthly_cost.get(month_key, Decimal('0')) + (record.normalized_thousand_dollars or Decimal('0'))
		monthly_usage[month_key] = monthly_usage.get(month_key, Decimal('0')) + (record.normalized_mwh or Decimal('0'))
		tariff_key = record.tariff_type or 'Unknown'
		tariff_breakdown[tariff_key] = tariff_breakdown.get(tariff_key, Decimal('0')) + (record.normalized_thousand_dollars or Decimal('0'))

	requires_normalization = records.filter(
		Q(original_energy_unit__isnull=False)
		& ~Q(original_energy_unit='')
		& ~Q(original_energy_unit__iexact='mwh')
		| Q(original_cost_unit__isnull=False)
		& ~Q(original_cost_unit='')
		& ~Q(original_cost_unit__iexact='thousand dollars')
	).distinct().count()

	failed_conversions = records.filter(
		issues__severity='error',
		issues__message__icontains='unit',
	).distinct().count()

	unknown_units = records.filter(
		issues__severity='error',
		issues__message__icontains='unknown',
	).distinct().count()

	unit_values = list(records.exclude(original_energy_unit='').values_list('original_energy_unit', flat=True))
	most_common_unit = None
	if unit_values:
		unit_counts = {}
		for unit in unit_values:
			unit_counts[unit] = unit_counts.get(unit, 0) + 1
		most_common_unit = max(unit_counts.items(), key=lambda item: item[1])[0]

	conversion_success = records.filter(
		normalized_mwh__isnull=False,
		normalized_thousand_dollars__isnull=False,
	).count()
	success_rate = 0
	if total_records:
		success_rate = round((conversion_success / total_records) * 100, 1)

	sector_units = {}
	for record in records.exclude(tariff_type=''):
		if record.original_energy_unit:
			sector_units.setdefault(record.tariff_type, set()).add(record.original_energy_unit)
	sector_mixed = [sector for sector, units in sector_units.items() if len(units) > 1]

	normalization_insights = []
	if total_records:
		percentage = round((requires_normalization / total_records) * 100, 1)
		normalization_insights.append(f"{percentage}% of uploaded records required unit normalization.")
	if sector_mixed:
		normalization_insights.append(f"{', '.join(sector_mixed)} contained mixed energy units.")
	if failed_conversions:
		normalization_insights.append(
			f"{failed_conversions} records failed normalization due to unknown or missing units."
		)

	recent_uploads = ImportBatch.objects.order_by('-upload_time')[:5]

	return Response(
		{
			'summary': {
				'total_thousand_dollars': str(total_thousand),
				'total_mwh': str(total_mwh),
				'uploaded_bills': records.count(),
				'failed_records': failed_count,
				'suspicious_records': suspicious_count,
			},
			'normalization_quality': {
				'total_records': total_records,
				'normalized_rows': requires_normalization,
				'failed_conversions': failed_conversions,
				'unknown_units': unknown_units,
				'most_common_unit': most_common_unit,
				'success_rate': success_rate,
			},
			'normalization_insights': normalization_insights,
			'monthly_cost_trend': [
				{'month': key, 'total_thousand_dollars': str(value)}
				for key, value in sorted(monthly_cost.items())
			],
			'monthly_usage_trend': [
				{'month': key, 'usage_mwh': str(value)}
				for key, value in sorted(monthly_usage.items())
			],
			'tariff_breakdown': [
				{'tariff_type': key, 'total_thousand_dollars': str(value)}
				for key, value in sorted(tariff_breakdown.items())
			],
			'recent_uploads': ImportBatchSerializer(recent_uploads, many=True).data,
		}
	)


class ImportBatchViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = ImportBatch.objects.order_by('-upload_time')
	serializer_class = ImportBatchSerializer


class NormalizedRecordViewSet(viewsets.ReadOnlyModelViewSet):
	serializer_class = NormalizedUtilityRecordSerializer

	def get_queryset(self):
		queryset = NormalizedUtilityRecord.objects.all().order_by('-created_at')
		status_filter = self.request.query_params.get('status')
		meter_query = self.request.query_params.get('meter_id')
		unit_filter = self.request.query_params.get('original_energy_unit')
		if status_filter:
			queryset = queryset.filter(status=status_filter)
		if meter_query:
			queryset = queryset.filter(meter_id__icontains=meter_query)
		if unit_filter:
			queryset = queryset.filter(original_energy_unit__iexact=unit_filter)
		return queryset

	@action(detail=True, methods=['post'])
	def approve(self, request, pk=None):
		record = self.get_object()
		if record.locked:
			return Response({'detail': 'Record is locked for audit.'}, status=status.HTTP_400_BAD_REQUEST)
		record.status = 'approved'
		record.locked = True
		record.approved_by = request.user
		record.approved_at = timezone.now()
		record.save(update_fields=['status', 'locked', 'approved_by', 'approved_at'])
		return Response(NormalizedUtilityRecordSerializer(record).data)

	@action(detail=True, methods=['post'])
	def reject(self, request, pk=None):
		record = self.get_object()
		if record.locked:
			return Response({'detail': 'Record is locked for audit.'}, status=status.HTTP_400_BAD_REQUEST)
		record.status = 'rejected'
		record.approved_by = request.user
		record.approved_at = timezone.now()
		record.save(update_fields=['status', 'approved_by', 'approved_at'])
		return Response(NormalizedUtilityRecordSerializer(record).data)


class ValidationIssueViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = ValidationIssue.objects.select_related('record').order_by('-created_at')
	serializer_class = ValidationIssueSerializer
