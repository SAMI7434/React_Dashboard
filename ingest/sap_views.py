import csv
import json
from io import TextIOWrapper
from decimal import Decimal
from datetime import datetime, timedelta
from collections import defaultdict

from django.db.models import Q, Sum, Count, Avg, F
from django.db.models.functions import TruncMonth
from django.conf import settings
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import (
    SAPImportBatch,
    RawSAPRecord,
    NormalizedSAPRecord,
    SAPValidationIssue,
    SAPApprovalLog,
)
from .sap_serializers import (
    SAPImportBatchSerializer,
    NormalizedSAPRecordSerializer,
    NormalizedSAPRecordDetailSerializer,
    SAPValidationIssueSerializer,
    SAPApprovalLogSerializer,
)


# Unit conversion factors to liters
UNIT_TO_LITERS = {
    'liters': Decimal('1'),
    'liter': Decimal('1'),
    'l': Decimal('1'),
    'gallons': Decimal('3.78541'),
    'gallon': Decimal('3.78541'),
    'gal': Decimal('3.78541'),
    'barrels': Decimal('158.987'),
    'barrel': Decimal('158.987'),
    'bbl': Decimal('158.987'),
    'kiloliters': Decimal('1000'),
    'kiloliter': Decimal('1000'),
    'kl': Decimal('1000'),
    'cubic meters': Decimal('1000'),
    'cubic meter': Decimal('1000'),
    'm3': Decimal('1000'),
}

# German column header mappings
GERMAN_COLUMN_MAPPINGS = {
    'werks': 'plant_code',
    'menge': 'quantity',
    'matnr': 'material_number',
    'datum': 'purchase_date',
    'lifnr': 'vendor_id',
    'name1': 'vendor_name',
    'bwart': 'fuel_type',
    'meins': 'unit',
    'preis': 'total_cost',
    'waers': 'currency',
    'belnr': 'invoice_number',
    'land1': 'country',
    'ort01': 'location_city',
    'regio': 'location_state',
}

# Logistics fuel purchases column mappings (alternative format)
LOGISTICS_COLUMN_MAPPINGS = {
    'fuel_purchase_id': 'invoice_number',
    'trip_id': 'trip_id',
    'truck_id': 'truck_id',
    'driver_id': 'driver_id',
    'purchase_date': 'purchase_date',
    'location_city': 'location_city',
    'location_state': 'location_state',
    'gallons': 'quantity',
    'price_per_gallon': 'cost_per_unit',
    'total_cost': 'total_cost',
    'fuel_card_number': 'vendor_id',
}

# Fuel type detection from context
FUEL_TYPE_DETECTION = {
    'DIESEL': 'Diesel',
    'DSL': 'Diesel',
    'GASOLINE': 'Gasoline',
    'PETROL': 'Gasoline',
    'UNLEADED': 'Gasoline',
    'JET': 'Jet Fuel',
    'AVIATION': 'Jet Fuel',
    'KEROSENE': 'Jet Fuel',
    'HEAVY': 'Heavy Fuel Oil',
    'HFO': 'Heavy Fuel Oil',
    'LNG': 'Natural Gas',
    'LPG': 'LPG',
    'PROPANE': 'LPG',
}


def normalize_quantity(value, unit):
    """Normalize quantity to liters."""
    if value is None:
        return None, 'liters'
    
    unit_lower = unit.lower().strip() if unit else ''
    factor = UNIT_TO_LITERS.get(unit_lower)
    
    if factor is None:
        return None, 'liters'
    
    normalized = value * factor
    return normalized, 'liters'


def detect_fuel_type(material_number, description=''):
    """Detect fuel type from material number or description."""
    material_upper = (material_number or '').upper()
    desc_upper = (description or '').upper()
    
    if any(x in material_upper or x in desc_upper for x in ['DIESEL', 'DSL', 'GASOIL']):
        return 'Diesel'
    if any(x in material_upper or x in desc_upper for x in ['GASOLINE', 'PETROL', 'UNLEADED', 'MOGAS']):
        return 'Gasoline'
    if any(x in material_upper or x in desc_upper for x in ['JET', 'AVIATION', 'KEROSENE', 'JET A1']):
        return 'Jet Fuel'
    if any(x in material_upper or x in desc_upper for x in ['HEAVY', 'HFO', 'FUEL OIL']):
        return 'Heavy Fuel Oil'
    if any(x in material_upper or x in desc_upper for x in ['LNG', 'NATURAL GAS']):
        return 'Natural Gas'
    if any(x in material_upper or x in desc_upper for x in ['LPG', 'PROPANE', 'BUTANE']):
        return 'LPG'
    
    return 'Other'


# Vendor mapping for logistics format (fuel card to vendor)
LOGISTICS_VENDOR_MAP = {
    'FC567161': {'id': 'VEND001', 'name': 'Shell Oil'},
    'FC717910': {'id': 'VEND002', 'name': 'Exxon Mobil'},
    'FC912816': {'id': 'VEND003', 'name': 'Chevron'},
    'FC776357': {'id': 'VEND004', 'name': 'BP America'},
    'FC391024': {'id': 'VEND005', 'name': 'Sunoco'},
    'FC277504': {'id': 'VEND006', 'name': 'ConocoPhillips'},
    'FC256663': {'id': 'VEND007', 'name': 'Valero'},
    'FC543608': {'id': 'VEND008', 'name': 'Marathon'},
    'FC484857': {'id': 'VEND009', 'name': 'Citgo'},
    'FC753360': {'id': 'VEND010', 'name': 'Tesoro'},
}

# State to plant code mapping
STATE_PLANT_MAP = {
    'TX': 'PLANT001', 'CA': 'PLANT002', 'FL': 'PLANT003',
    'NY': 'PLANT004', 'IL': 'PLANT005', 'PA': 'PLANT001',
    'OH': 'PLANT002', 'GA': 'PLANT003', 'NC': 'PLANT004',
    'MI': 'PLANT005', 'NJ': 'PLANT001', 'VA': 'PLANT002',
    'WA': 'PLANT003', 'AZ': 'PLANT004', 'MA': 'PLANT005',
    'TN': 'PLANT001', 'IN': 'PLANT002', 'MO': 'PLANT003',
    'MD': 'PLANT004', 'WI': 'PLANT005', 'CO': 'PLANT001',
    'MN': 'PLANT002', 'SC': 'PLANT003', 'AL': 'PLANT004',
    'LA': 'PLANT005', 'KY': 'PLANT001', 'OR': 'PLANT002',
    'OK': 'PLANT003', 'CT': 'PLANT004', 'UT': 'PLANT005',
    'NV': 'PLANT001', 'AR': 'PLANT002', 'MS': 'PLANT003',
    'KS': 'PLANT004', 'NM': 'PLANT005', 'NE': 'PLANT001',
    'WV': 'PLANT002', 'ID': 'PLANT003', 'HI': 'PLANT004',
    'NH': 'PLANT005', 'ME': 'PLANT001', 'MT': 'PLANT002',
    'RI': 'PLANT003', 'DE': 'PLANT004', 'SD': 'PLANT005',
    'ND': 'PLANT001', 'AK': 'PLANT002', 'VT': 'PLANT003',
    'WY': 'PLANT004', 'IA': 'PLANT005',
}


def detect_format(row):
    """Detect if the row is in logistics format or standard SAP format."""
    if 'fuel_purchase_id' in row or 'gallons' in row or 'fuel_card_number' in row:
        return 'logistics'
    return 'standard'


def get_vendor_from_fuel_card(fuel_card_number):
    """Get vendor info from fuel card number."""
    return LOGISTICS_VENDOR_MAP.get(fuel_card_number, {
        'id': f"VEND{fuel_card_number[2:]}" if fuel_card_number and len(fuel_card_number) > 2 else 'VEND000',
        'name': 'Unknown Vendor'
    })


def get_plant_code(state, row_num):
    """Get plant code from state or generate one."""
    return STATE_PLANT_MAP.get(state, f'PLANT{((row_num % 5) + 1):03d}')


def detect_fuel_type_from_price(price_per_gallon):
    """Detect fuel type based on price per gallon."""
    try:
        price = float(price_per_gallon)
        if price < 3.5:
            return 'Diesel'
        elif price < 4.5:
            return 'Gasoline'
        else:
            return 'Jet Fuel'
    except:
        return 'Diesel'


@api_view(['POST'])
def sap_upload_csv_view(request):
    """Upload and process SAP fuel procurement CSV file.
    
    Supports both standard SAP format and logistics fuel_purchases.csv format.
    """
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    upload_file = request.FILES['file']
    batch = SAPImportBatch.objects.create(
        file_name=upload_file.name,
        uploaded_by=request.user,
        status='processing',
    )
    
    created_records = 0
    error_rows = 0
    warning_rows = 0
    
    # Thresholds for anomaly detection
    price_spike_threshold = Decimal('5.0')  # $5 per liter threshold
    quantity_anomaly_threshold = Decimal('10000')  # 10000 liters threshold
    
    try:
        text_stream = TextIOWrapper(upload_file.file, encoding='utf-8-sig')
        reader = csv.DictReader(text_stream)
        
        # Track invoice numbers for duplicate detection
        seen_invoices = {}
        
        # Detect format from first row
        first_row = None
        format_type = 'standard'
        
        for index, row in enumerate(reader, start=1):
            issues = []
            
            # Detect format on first row
            if index == 1:
                format_type = detect_format(row)
            
            # Map headers based on format
            mapped_row = {}
            
            if format_type == 'logistics':
                # Handle logistics format (fuel_purchases.csv)
                for key, value in row.items():
                    clean_key = key.strip().lower()
                    if clean_key in LOGISTICS_COLUMN_MAPPINGS:
                        mapped_row[LOGISTICS_COLUMN_MAPPINGS[clean_key]] = value
                    else:
                        mapped_row[clean_key] = value
                
                # Generate missing SAP-required fields
                fuel_card = mapped_row.get('vendor_id', '')
                vendor_info = get_vendor_from_fuel_card(fuel_card)
                mapped_row['vendor_id'] = vendor_info['id']
                mapped_row['vendor_name'] = vendor_info['name']
                
                # Assign plant code based on state
                state = mapped_row.get('location_state', '')
                mapped_row['plant_code'] = get_plant_code(state, index)
                
                # Generate material number based on fuel type
                price_per_gallon = mapped_row.get('cost_per_unit', '0')
                fuel_type = detect_fuel_type_from_price(price_per_gallon)
                mapped_row['fuel_type'] = fuel_type
                mapped_row['material_number'] = f"{fuel_type.upper().replace(' ', '-')}-001"
                
                # Convert gallons to liters
                gallons_str = mapped_row.get('quantity', '0')
                try:
                    gallons = Decimal(str(gallons_str).replace(',', '.'))
                    liters = gallons * Decimal('3.78541')
                    mapped_row['quantity'] = str(liters)
                    mapped_row['unit'] = 'liters'
                except:
                    pass
                
                # Set country if not present
                if not mapped_row.get('country'):
                    mapped_row['country'] = 'USA'
                
                # Use cost_per_unit as cost_per_unit (already set from price_per_gallon)
                # But we need to recalculate based on liters
                total_cost_str = mapped_row.get('total_cost', '0')
                try:
                    total_cost = Decimal(str(total_cost_str).replace(',', '.'))
                    if gallons and gallons > 0:
                        cost_per_liter = total_cost / liters
                        mapped_row['cost_per_unit'] = str(cost_per_liter)
                except:
                    pass
            else:
                # Handle standard SAP format and German headers
                for key, value in row.items():
                    clean_key = key.strip().lower()
                    if clean_key in GERMAN_COLUMN_MAPPINGS:
                        mapped_row[GERMAN_COLUMN_MAPPINGS[clean_key]] = value
                    else:
                        mapped_row[clean_key] = value
            
            # Extract fields
            material_number = (mapped_row.get('material_number') or mapped_row.get('matnr') or '').strip()
            plant_code = (mapped_row.get('plant_code') or mapped_row.get('werks') or '').strip()
            vendor_id = (mapped_row.get('vendor_id') or mapped_row.get('lifnr') or '').strip()
            vendor_name = (mapped_row.get('vendor_name') or mapped_row.get('name1') or '').strip()
            invoice_number = (mapped_row.get('invoice_number') or mapped_row.get('belnr') or '').strip()
            
            # Parse purchase date
            purchase_date_str = (mapped_row.get('purchase_date') or mapped_row.get('datum') or '').strip()
            purchase_date = None
            if purchase_date_str:
                for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%m/%d/%Y', '%Y%m%d']:
                    try:
                        purchase_date = datetime.strptime(purchase_date_str, fmt).date()
                        break
                    except ValueError:
                        continue
                if purchase_date is None:
                    issues.append(('error', 'Invalid or missing purchase date.'))
            
            # Parse quantity
            quantity_str = mapped_row.get('quantity') or mapped_row.get('menge') or '0'
            try:
                quantity = Decimal(str(quantity_str).replace(',', '.'))
            except:
                quantity = None
                issues.append(('error', 'Invalid quantity value.'))
            
            # Get unit
            unit = (mapped_row.get('unit') or mapped_row.get('meins') or 'liters').strip()
            
            # Normalize quantity
            normalized_qty, normalized_unit = normalize_quantity(quantity, unit)
            if quantity is not None and normalized_qty is None:
                issues.append(('error', f'Unknown unit: {unit}'))
            
            # Parse cost
            cost_str = mapped_row.get('total_cost') or mapped_row.get('preis') or '0'
            try:
                total_cost = Decimal(str(cost_str).replace(',', '.'))
            except:
                total_cost = None
                issues.append(('error', 'Invalid cost value.'))
            
            # Get currency
            currency = (mapped_row.get('currency') or mapped_row.get('waers') or 'USD').strip()
            
            # Calculate cost per unit
            cost_per_unit = None
            if total_cost and normalized_qty and normalized_qty > 0:
                cost_per_unit = total_cost / normalized_qty
            
            # Get location data
            country = (mapped_row.get('country') or mapped_row.get('land1') or '').strip()
            location_city = (mapped_row.get('location_city') or mapped_row.get('ort01') or '').strip()
            location_state = (mapped_row.get('location_state') or mapped_row.get('regio') or '').strip()
            
            # Detect fuel type
            fuel_type = detect_fuel_type(material_number, mapped_row.get('description', ''))
            
            # Validation checks
            if not plant_code:
                issues.append(('error', 'Missing plant code (WERKS).'))
            
            if not vendor_id:
                issues.append(('warning', 'Missing vendor ID.'))
            
            if total_cost is not None and total_cost < 0:
                issues.append(('warning', 'Negative total cost detected.'))
            
            # Duplicate invoice detection
            if invoice_number and invoice_number in seen_invoices:
                issues.append(('error', f'Duplicate invoice number: {invoice_number}'))
            elif invoice_number:
                seen_invoices[invoice_number] = index
            
            # Price spike detection
            if cost_per_unit and cost_per_unit > price_spike_threshold:
                issues.append(('warning', f'Price spike detected: ${cost_per_unit:.2f}/liter'))
            
            # Quantity anomaly detection
            if normalized_qty and normalized_qty > quantity_anomaly_threshold:
                issues.append(('warning', f'Abnormally high quantity: {normalized_qty:.0f} liters'))
            
            # Suspicious vendor detection (simplified)
            if vendor_id and len(vendor_id) < 3:
                issues.append(('warning', 'Suspicious vendor ID format.'))
            
            # Create raw record
            raw_record = RawSAPRecord.objects.create(
                import_batch=batch,
                row_number=index,
                raw_data=dict(row),
            )
            
            # Create normalized record
            normalized = NormalizedSAPRecord.objects.create(
                import_batch=batch,
                raw_record=raw_record,
                material_number=material_number,
                plant_code=plant_code,
                vendor_id=vendor_id,
                vendor_name=vendor_name,
                purchase_date=purchase_date,
                invoice_number=invoice_number,
                fuel_type=fuel_type,
                original_quantity=quantity,
                original_unit=unit,
                normalized_quantity=normalized_qty,
                normalized_unit=normalized_unit,
                total_cost=total_cost,
                cost_per_unit=cost_per_unit,
                currency=currency,
                country=country,
                location_city=location_city,
                location_state=location_state,
            )
            
            # Create validation issues
            for severity, message in issues:
                SAPValidationIssue.objects.create(
                    record=normalized,
                    severity=severity,
                    issue_type='duplicate_invoice' if 'Duplicate' in message else 
                               'price_spike' if 'Price spike' in message else
                               'quantity_anomaly' if 'Abnormally' in message else
                               'missing_plant' if 'Missing plant' in message else
                               'invalid_date' if 'Invalid' in message and 'date' in message.lower() else
                               'invalid_unit' if 'Unknown unit' in message else
                               'negative_amount' if 'Negative' in message else
                               'unknown_vendor' if 'Missing vendor' in message else
                               'suspicious_vendor' if 'Suspicious' in message else
                               'missing_plant',
                    message=message,
                )
            
            if any(severity == 'error' for severity, _ in issues):
                error_rows += 1
            if any(severity == 'warning' for severity, _ in issues):
                warning_rows += 1
            
            created_records += 1
        
        batch.total_records = created_records
        batch.failed_records = error_rows
        batch.suspicious_records = warning_rows
        batch.status = 'completed'
        batch.save()
        
    except Exception as e:
        batch.status = 'failed'
        batch.save()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'batch': SAPImportBatchSerializer(batch).data,
        'records_created': created_records,
        'failed_records': error_rows,
        'suspicious_records': warning_rows,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def sap_dashboard_view(request):
    """SAP Fuel & Procurement Analytics Dashboard summary."""
    records = NormalizedSAPRecord.objects.all()
    
    # KPI calculations
    total_fuel_spend = records.filter(status__in=['pending', 'approved']).aggregate(
        sum=Sum('total_cost')
    )['sum'] or Decimal('0')
    
    total_fuel_quantity = records.filter(status__in=['pending', 'approved']).aggregate(
        sum=Sum('normalized_quantity')
    )['sum'] or Decimal('0')
    
    total_vendors = records.values('vendor_id').distinct().count()
    total_plants = records.values('plant_code').distinct().count()
    
    suspicious_count = records.filter(sap_issues__severity='warning').distinct().count()
    failed_count = records.filter(sap_issues__severity='error').distinct().count()
    pending_approvals = records.filter(status='pending').count()
    
    # Monthly fuel spend trend - use SQLite-compatible approach
    use_sqlite = settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'
    
    if use_sqlite:
        # For SQLite, manually extract year-month
        monthly_spend = []
        filtered_records = records.filter(
            purchase_date__isnull=False,
            status__in=['pending', 'approved']
        )
        month_data = {}
        for r in filtered_records:
            if r.purchase_date:
                month_key = r.purchase_date.strftime('%Y-%m')
                if month_key not in month_data:
                    month_data[month_key] = {'total_spend': Decimal('0'), 'total_quantity': Decimal('0')}
                month_data[month_key]['total_spend'] += r.total_cost or Decimal('0')
                month_data[month_key]['total_quantity'] += r.normalized_quantity or Decimal('0')
        for month_key in sorted(month_data.keys())[-12:]:
            monthly_spend.append({
                'month': month_key,
                'total_spend': str(month_data[month_key]['total_spend']),
                'total_quantity': str(month_data[month_key]['total_quantity'])
            })
    else:
        monthly_spend = records.filter(
            purchase_date__isnull=False,
            status__in=['pending', 'approved']
        ).annotate(
            month=TruncMonth('purchase_date')
        ).values('month').annotate(
            total_spend=Sum('total_cost'),
            total_quantity=Sum('normalized_quantity')
        ).order_by('month')[:12]
    
    # Plant-wise procurement cost
    plant_costs = records.filter(
        plant_code__isnull=False,
        status__in=['pending', 'approved']
    ).values('plant_code').annotate(
        total_cost=Sum('total_cost'),
        total_quantity=Sum('normalized_quantity'),
        avg_cost=Avg('cost_per_unit')
    ).order_by('-total_cost')[:10]
    
    # Vendor spend ranking
    vendor_spend = records.filter(
        vendor_id__isnull=False,
        status__in=['pending', 'approved']
    ).values('vendor_id', 'vendor_name').annotate(
        total_spend=Sum('total_cost'),
        transaction_count=Count('id')
    ).order_by('-total_spend')[:10]
    
    # Fuel type distribution
    fuel_type_dist = records.filter(
        fuel_type__isnull=False,
        status__in=['pending', 'approved']
    ).values('fuel_type').annotate(
        total_quantity=Sum('normalized_quantity'),
        total_cost=Sum('total_cost')
    ).order_by('-total_quantity')
    
    # Country distribution
    country_dist = records.filter(
        country__isnull=False,
        status__in=['pending', 'approved']
    ).values('country').annotate(
        total_spend=Sum('total_cost'),
        record_count=Count('id')
    ).order_by('-total_spend')[:10]
    
    # Validation error breakdown
    error_breakdown = SAPValidationIssue.objects.filter(
        record__status__in=['pending', 'approved']
    ).values('issue_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Approval status overview
    status_overview = records.values('status').annotate(count=Count('id'))
    
    # Generate smart insights
    insights = []
    
    # Price spike insights
    price_spikes = SAPValidationIssue.objects.filter(issue_type='price_spike').count()
    if price_spikes > 0:
        insights.append(f"{price_spikes} price spike(s) detected in fuel procurement.")
    
    # Plant with highest spend increase
    if plant_costs:
        top_plant = plant_costs[0]
        insights.append(f"Plant {top_plant['plant_code']} has highest procurement cost at ${top_plant['total_cost']:.2f}")
    
    # Vendor insights
    if vendor_spend:
        top_vendor = vendor_spend[0]
        vendor_name = top_vendor['vendor_name'] or top_vendor['vendor_id']
        insights.append(f"Vendor {vendor_name} has highest spend at ${top_vendor['total_spend']:.2f}")
    
    # Duplicate invoice insights
    duplicates = SAPValidationIssue.objects.filter(issue_type='duplicate_invoice').count()
    if duplicates > 0:
        insights.append(f"{duplicates} duplicate invoice(s) detected.")
    
    # Quantity anomaly insights
    anomalies = SAPValidationIssue.objects.filter(issue_type='quantity_anomaly').count()
    if anomalies > 0:
        insights.append(f"{anomalies} abnormal fuel quantity record(s) detected.")
    
    return Response({
        'summary': {
            'total_fuel_spend': str(total_fuel_spend),
            'total_fuel_quantity': str(total_fuel_quantity),
            'total_vendors': total_vendors,
            'total_plants': total_plants,
            'suspicious_records': suspicious_count,
            'failed_records': failed_count,
            'pending_approvals': pending_approvals,
        },
        'monthly_spend_trend': [
            {
                'month': item.get('month', item.get('month', '')),
                'total_spend': str(item.get('total_spend', '0')),
                'total_quantity': str(item.get('total_quantity', '0')),
            }
            for item in monthly_spend
        ],
        'plant_costs': [
            {
                'plant_code': item['plant_code'],
                'total_cost': str(item['total_cost'] or Decimal('0')),
                'total_quantity': str(item['total_quantity'] or Decimal('0')),
                'avg_cost_per_liter': str(item['avg_cost'] or Decimal('0')),
            }
            for item in plant_costs
        ],
        'vendor_spend': [
            {
                'vendor_id': item['vendor_id'],
                'vendor_name': item['vendor_name'] or item['vendor_id'],
                'total_spend': str(item['total_spend'] or Decimal('0')),
                'transaction_count': item['transaction_count'],
            }
            for item in vendor_spend
        ],
        'fuel_type_distribution': [
            {
                'fuel_type': item['fuel_type'] or 'Unknown',
                'total_quantity': str(item['total_quantity'] or Decimal('0')),
                'total_cost': str(item['total_cost'] or Decimal('0')),
            }
            for item in fuel_type_dist
        ],
        'country_distribution': [
            {
                'country': item['country'] or 'Unknown',
                'total_spend': str(item['total_spend'] or Decimal('0')),
                'record_count': item['record_count'],
            }
            for item in country_dist
        ],
        'error_breakdown': [
            {
                'issue_type': item['issue_type'],
                'count': item['count'],
            }
            for item in error_breakdown
        ],
        'status_overview': [
            {
                'status': item['status'],
                'count': item['count'],
            }
            for item in status_overview
        ],
        'insights': insights,
    })


class SAPRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for SAP procurement records."""
    serializer_class = NormalizedSAPRecordSerializer
    
    def get_queryset(self):
        queryset = NormalizedSAPRecord.objects.all().order_by('-created_at')
        
        # Filters
        status_filter = self.request.query_params.get('status')
        plant_filter = self.request.query_params.get('plant_code')
        vendor_filter = self.request.query_params.get('vendor_id')
        fuel_type_filter = self.request.query_params.get('fuel_type')
        has_issues = self.request.query_params.get('has_issues')
        search = self.request.query_params.get('search')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if plant_filter:
            queryset = queryset.filter(plant_code__icontains=plant_filter)
        if vendor_filter:
            queryset = queryset.filter(vendor_id__icontains=vendor_filter)
        if fuel_type_filter:
            queryset = queryset.filter(fuel_type__iexact=fuel_type_filter)
        if has_issues == 'true':
            queryset = queryset.filter(sap_issues__isnull=False).distinct()
        elif has_issues == 'false':
            queryset = queryset.filter(sap_issues__isnull=True)
        if search:
            queryset = queryset.filter(
                Q(material_number__icontains=search) |
                Q(plant_code__icontains=search) |
                Q(vendor_id__icontains=search) |
                Q(vendor_name__icontains=search) |
                Q(invoice_number__icontains=search)
            )
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NormalizedSAPRecordDetailSerializer
        return NormalizedSAPRecordSerializer
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a procurement record."""
        record = self.get_object()
        if record.locked:
            return Response({'detail': 'Record is locked for audit.'}, status=status.HTTP_400_BAD_REQUEST)
        
        previous_status = record.status
        record.status = 'approved'
        record.locked = True
        record.approved_by = request.user
        record.approved_at = timezone.now()
        record.save(update_fields=['status', 'locked', 'approved_by', 'approved_at'])
        
        # Log the approval
        SAPApprovalLog.objects.create(
            record=record,
            user=request.user,
            action='approved',
            notes=request.data.get('notes', ''),
            previous_status=previous_status,
            new_status='approved',
        )
        
        return Response(NormalizedSAPRecordSerializer(record).data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a procurement record."""
        record = self.get_object()
        if record.locked:
            return Response({'detail': 'Record is locked for audit.'}, status=status.HTTP_400_BAD_REQUEST)
        
        previous_status = record.status
        record.status = 'rejected'
        record.approved_by = request.user
        record.approved_at = timezone.now()
        record.save(update_fields=['status', 'approved_by', 'approved_at'])
        
        # Log the rejection
        SAPApprovalLog.objects.create(
            record=record,
            user=request.user,
            action='rejected',
            notes=request.data.get('notes', ''),
            previous_status=previous_status,
            new_status='rejected',
        )
        
        return Response(NormalizedSAPRecordSerializer(record).data)
    
    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """Add a note to a procurement record."""
        record = self.get_object()
        notes = request.data.get('notes', '')
        
        SAPApprovalLog.objects.create(
            record=record,
            user=request.user,
            action='note_added',
            notes=notes,
            previous_status=record.status,
            new_status=record.status,
        )
        
        return Response({'detail': 'Note added successfully.'})
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export records as CSV."""
        queryset = self.get_queryset()[:1000]  # Limit to 1000 records
        
        response = Response(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sap_procurement_records.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Material Number', 'Plant Code', 'Vendor ID', 'Vendor Name',
            'Purchase Date', 'Invoice Number', 'Fuel Type', 'Quantity', 'Unit',
            'Total Cost', 'Cost Per Unit', 'Currency', 'Country', 'Status'
        ])
        
        for record in queryset:
            writer.writerow([
                record.id,
                record.material_number,
                record.plant_code,
                record.vendor_id,
                record.vendor_name,
                record.purchase_date,
                record.invoice_number,
                record.fuel_type,
                record.normalized_quantity,
                record.normalized_unit,
                record.total_cost,
                record.cost_per_unit,
                record.currency,
                record.country,
                record.status,
            ])
        
        return response


class SAPValidationIssueViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for SAP validation issues."""
    serializer_class = SAPValidationIssueSerializer
    
    def get_queryset(self):
        queryset = SAPValidationIssue.objects.select_related('record').order_by('-created_at')
        
        severity_filter = self.request.query_params.get('severity')
        issue_type_filter = self.request.query_params.get('issue_type')
        
        if severity_filter:
            queryset = queryset.filter(severity=severity_filter)
        if issue_type_filter:
            queryset = queryset.filter(issue_type=issue_type_filter)
        
        return queryset


class SAPApprovalLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for SAP approval logs."""
    serializer_class = SAPApprovalLogSerializer
    
    def get_queryset(self):
        queryset = SAPApprovalLog.objects.select_related('record', 'user').order_by('-created_at')
        record_filter = self.request.query_params.get('record_id')
        
        if record_filter:
            queryset = queryset.filter(record_id=record_filter)
        
        return queryset


class SAPImportBatchViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for SAP import batches."""
    serializer_class = SAPImportBatchSerializer
    
    def get_queryset(self):
        return SAPImportBatch.objects.order_by('-upload_time')