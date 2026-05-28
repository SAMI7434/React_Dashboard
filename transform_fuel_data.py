#!/usr/bin/env python3
"""
Fuel Purchases Data Transformer
Converts logistics fuel_purchases.csv to SAP procurement format
"""

import csv
import os
from datetime import datetime
from decimal import Decimal
import random

# Configuration
INPUT_FILE = 'logistic data set/fuel_purchases.csv'
OUTPUT_FILE = 'logistic data set/fuel_purchases_sap_format.csv'

# Plant codes mapping (you can customize these)
PLANT_CODES = ['PLANT001', 'PLANT002', 'PLANT003', 'PLANT004', 'PLANT005']

# Vendor mapping (fuel card to vendor)
VENDOR_MAP = {
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

# Material numbers based on fuel type detection
MATERIAL_NUMBERS = {
    'Diesel': 'DIESEL-001',
    'Gasoline': 'GASOLINE-001',
    'Jet Fuel': 'JETFUEL-001',
    'Other': 'FUEL-OTHER-001'
}

def detect_fuel_type_from_price(price_per_gallon):
    """Detect fuel type based on price per gallon (approximate)"""
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

def transform_data():
    """Transform fuel purchases data to SAP format"""
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file '{INPUT_FILE}' not found!")
        return
    
    transformed_records = []
    error_records = []
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
            try:
                # Extract original data
                fuel_purchase_id = row.get('fuel_purchase_id', '').strip()
                trip_id = row.get('trip_id', '').strip()
                truck_id = row.get('truck_id', '').strip()
                driver_id = row.get('driver_id', '').strip()
                purchase_date = row.get('purchase_date', '').strip()
                location_city = row.get('location_city', '').strip()
                location_state = row.get('location_state', '').strip()
                gallons = row.get('gallons', '').strip()
                price_per_gallon = row.get('price_per_gallon', '').strip()
                total_cost = row.get('total_cost', '').strip()
                fuel_card_number = row.get('fuel_card_number', '').strip()
                
                # Skip if essential data is missing
                if not fuel_purchase_id or not purchase_date or not gallons or not total_cost:
                    error_records.append({
                        'row': row_num,
                        'fuel_purchase_id': fuel_purchase_id,
                        'reason': 'Missing essential data (ID, date, gallons, or cost)'
                    })
                    continue
                
                # Detect fuel type
                fuel_type = detect_fuel_type_from_price(price_per_gallon)
                material_number = MATERIAL_NUMBERS.get(fuel_type, 'FUEL-OTHER-001')
                
                # Get vendor info
                vendor_info = VENDOR_MAP.get(fuel_card_number)
                if vendor_info:
                    vendor_id = vendor_info['id']
                    vendor_name = vendor_info['name']
                else:
                    # Generate vendor ID from fuel card if not in map
                    vendor_id = f"VEND{fuel_card_number[2:]}" if fuel_card_number else 'VEND000'
                    vendor_name = 'Unknown Vendor'
                
                # Assign plant code (you can customize this logic)
                # For demo, we'll assign based on location state
                plant_code = assign_plant_code(location_state, row_num)
                
                # Convert gallons to liters for SAP (SAP uses liters as standard)
                try:
                    gallons_decimal = Decimal(gallons)
                    liters = gallons_decimal * Decimal('3.78541')
                    quantity = float(liters)
                except:
                    quantity = 0
                    error_records.append({
                        'row': row_num,
                        'fuel_purchase_id': fuel_purchase_id,
                        'reason': f'Invalid gallons value: {gallons}'
                    })
                
                # Calculate cost per liter
                try:
                    total_cost_decimal = Decimal(total_cost)
                    cost_per_liter = float(total_cost_decimal / liters) if liters > 0 else 0
                except:
                    cost_per_liter = 0
                
                # Format purchase date for SAP
                formatted_date = format_date_for_sap(purchase_date)
                
                # Create SAP format record
                sap_record = {
                    'material_number': material_number,
                    'plant_code': plant_code,
                    'vendor_id': vendor_id,
                    'vendor_name': vendor_name,
                    'purchase_date': formatted_date,
                    'invoice_number': fuel_purchase_id,  # Use fuel purchase ID as invoice number
                    'fuel_type': fuel_type,
                    'quantity': f"{quantity:.4f}",
                    'unit': 'liters',
                    'total_cost': total_cost,
                    'cost_per_unit': f"{cost_per_liter:.4f}",
                    'currency': 'USD',
                    'country': 'USA',
                    'location_city': location_city,
                    'location_state': location_state,
                    # Keep original data for reference
                    'original_fuel_purchase_id': fuel_purchase_id,
                    'original_trip_id': trip_id,
                    'original_truck_id': truck_id,
                    'original_driver_id': driver_id,
                    'original_gallons': gallons,
                    'original_price_per_gallon': price_per_gallon,
                    'original_fuel_card_number': fuel_card_number,
                }
                
                transformed_records.append(sap_record)
                
            except Exception as e:
                error_records.append({
                    'row': row_num,
                    'fuel_purchase_id': row.get('fuel_purchase_id', 'UNKNOWN'),
                    'reason': str(e)
                })
    
    # Write transformed data to new CSV
    if transformed_records:
        write_sap_csv(transformed_records)
        print(f"✅ Successfully transformed {len(transformed_records)} records")
        print(f"📁 Output file: {OUTPUT_FILE}")
        
        if error_records:
            print(f"\n⚠️  {len(error_records)} records had issues:")
            for error in error_records[:5]:  # Show first 5 errors
                print(f"   Row {error['row']}: {error['reason']}")
            if len(error_records) > 5:
                print(f"   ... and {len(error_records) - 5} more")
    else:
        print("❌ No records were transformed successfully")

def assign_plant_code(state, row_num):
    """Assign plant code based on state or row number"""
    # Simple mapping - you can customize this
    state_plant_map = {
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
    
    return state_plant_map.get(state, f'PLANT{((row_num % 5) + 1):03d}')

def format_date_for_sap(date_str):
    """Format date string to SAP-compatible format (YYYY-MM-DD)"""
    if not date_str:
        return ''
    
    # Try multiple date formats
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y%m%d',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # If no format works, return original
    return date_str

def write_sap_csv(records):
    """Write transformed records to SAP format CSV"""
    
    fieldnames = [
        'material_number', 'plant_code', 'vendor_id', 'vendor_name',
        'purchase_date', 'invoice_number', 'fuel_type',
        'quantity', 'unit', 'total_cost', 'cost_per_unit', 'currency',
        'country', 'location_city', 'location_state',
        'original_fuel_purchase_id', 'original_trip_id',
        'original_truck_id', 'original_driver_id',
        'original_gallons', 'original_price_per_gallon',
        'original_fuel_card_number'
    ]
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

if __name__ == '__main__':
    print("🚀 Fuel Purchases Data Transformer")
    print("=" * 50)
    print(f"Input:  {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}")
    print("=" * 50)
    
    transform_data()
    
    print("\n✅ Transformation complete!")
    print("\n📊 Next Steps:")
    print("1. Review the transformed file: fuel_purchases_sap_format.csv")
    print("2. Upload to SAP dashboard using the upload endpoint")
    print("3. Check for any validation warnings in the dashboard")