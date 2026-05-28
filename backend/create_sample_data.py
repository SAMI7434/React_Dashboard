import os
import sys
import django
from datetime import date, datetime
from decimal import Decimal

# Setup Django environment
sys.path.append('/app')  # Adjust if needed
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ingest.models import SapRawRecord, UtilityRawRecord, TravelRawRecord, NormalizedRecord

def create_sample_data():
    # Clear existing data (optional)
    # NormalizedRecord.objects.all().delete()
    # SapRawRecord.objects.all().delete()
    # UtilityRawRecord.objects.all().delete()
    # TravelRawRecord.objects.all().delete()

    # Create a SAP raw record
    sap_raw = SapRawRecord.objects.create(
        sap_document_number='SAP456789',
        posting_date=date(2026, 5, 15),
        document_type='Invoice',
        vendor_customer_code='VEND12345',
        amount=Decimal('1250.00'),
        currency='USD',
        gl_account='400000',
        cost_center='CC123',
        profit_center='PC456',
        tax_code='V0',
        reference='PO98765',
        raw_data='{"document_number": "SAP456789", "posting_date": "2026-05-15", ...}'
    )

    # Create a Utility raw record
    utility_raw = UtilityRawRecord.objects.create(
        account_number='ACC987654321',
        meter_number='MTR654321',
        service_address='123 Main St, Anytown, USA',
        reading_date=date(2026, 5, 20),
        reading_value=Decimal('543.2'),
        unit='kWh',
        rate_plan='Residential Tiered',
        amount=Decimal('89.45'),
        billing_period_start=date(2026, 4, 21),
        billing_period_end=date(2026, 5, 20),
        raw_data='{"account_number": "ACC987654321", ...}'
    )

    # Create a Travel raw record
    travel_raw = TravelRawRecord.objects.create(
        expense_id='EXP789012',
        employee_id='EMP456',
        expense_date=date(2026, 5, 10),
        expense_type='Airfare',
        amount=Decimal('350.00'),
        currency='USD',
        vendor='Delta Airlines',
        description='Flight from NYC to LA for conference',
        receipt_url='https://example.com/receipts/exp789012.pdf',
        approval_status='Approved',
        raw_data='{"expense_id": "EXP789012", ...}'
    )

    # Create normalized records from the raw records (simulating processing)
    # For SAP
    norm_sap = NormalizedRecord.objects.create(
        source_type='SAP',
        sap_record=sap_raw,
        transaction_date=sap_raw.posting_date,
        amount=sap_raw.amount,
        currency=sap_raw.currency,
        description=f"SAP Invoice {sap_raw.sap_document_number} to {sap_raw.vendor_customer_code}",
        category='SAP Invoice',
        status='pending'  # waiting for review
    )

    # For Utility
    norm_utility = NormalizedRecord.objects.create(
        source_type='Utility',
        utility_record=utility_raw,
        transaction_date=utility_raw.reading_date,
        amount=utility_raw.amount,
        currency='USD',  # utility amounts are usually in local currency
        description=f"Electricity usage for {utility_raw.service_address} on {utility_raw.reading_date}",
        category='Electricity Utility',
        status='pending'
    )

    # For Travel
    norm_travel = NormalizedRecord.objects.create(
        source_type='Travel',
        travel_record=travel_raw,
        transaction_date=travel_raw.expense_date,
        amount=travel_raw.amount,
        currency=travel_raw.currency,
        description=f"{travel_raw.expense_type}: {travel_raw.description}",
        category='Travel Expense',
        status='pending'
    )

    # Create a failed normalized record (example: SAP with invalid amount)
    sap_raw_fail = SapRawRecord.objects.create(
        sap_document_number='SAP111111',
        posting_date=date(2026, 5, 1),
        document_type='Invoice',
        vendor_customer_code='VEND99999',
        amount=Decimal('-500.00'),  # Negative amount might be invalid for this context
        currency='USD',
        gl_account='400000',
        cost_center='',
        profit_center='',
        tax_code='V0',
        reference='',
        raw_data='{"document_number": "SAP111111", ...}'
    )
    norm_sap_fail = NormalizedRecord.objects.create(
        source_type='SAP',
        sap_record=sap_raw_fail,
        transaction_date=sap_raw_fail.posting_date,
        amount=sap_raw_fail.amount,
        currency=sap_raw_fail.currency,
        description=f"SAP Invoice {sap_raw_fail.sap_document_number} - NEGATIVE AMOUNT",
        category='SAP Invoice',
        status='failed'  # processing failed due to negative amount
    )

    # Create a suspicious normalized record (example: utility with very high usage)
    utility_raw_susp = UtilityRawRecord.objects.create(
        account_number='ACC111222333',
        meter_number='MTR999888',
        service_address='456 Oak Ave, Somewhere, USA',
        reading_date=date(2026, 5, 18),
        reading_value=Decimal('50000'),  # 50,000 kWh is suspiciously high for a residential meter
        unit='kWh',
        rate_plan='Residential',
        amount=Decimal('850.00'),
        billing_period_start=date(2026, 4, 19),
        billing_period_end=date(2026, 5, 18),
        raw_data='{"account_number": "ACC111222333", ...}'
    )
    norm_utility_susp = NormalizedRecord.objects.create(
        source_type='Utility',
        utility_record=utility_raw_susp,
        transaction_date=utility_raw_susp.reading_date,
        amount=utility_raw_susp.amount,
        currency='USD',
        description=f"High electricity usage: {utility_raw_susp.reading_value} {utility_raw_susp.unit}",
        category='Electricity Utility',
        status='suspicious'
    )

    print("Sample data created successfully.")
    print(f"SAP raw records: {SapRawRecord.objects.count()}")
    print(f"Utility raw records: {UtilityRawRecord.objects.count()}")
    print(f"Travel raw records: {TravelRawRecord.objects.count()}")
    print(f"Normalized records: {NormalizedRecord.objects.count()}")

if __name__ == '__main__':
    create_sample_data()