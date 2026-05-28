# SAP Fuel Procurement Dashboard - Data Upload Guide

## 📋 Overview

This guide explains how to upload fuel purchase data from your logistics dataset to the SAP procurement dashboard. The system now supports **both** standard SAP format and your original logistics `fuel_purchases.csv` format.

## 🔍 Problem Analysis

Your original `fuel_purchases.csv` file was missing critical SAP-required fields:
- **Plant Code** (WERKS) - Required by SAP
- **Material Number** (MATNR) - Required by SAP  
- **Vendor ID** (LIFNR) - Required by SAP
- **Vendor Name** (NAME1) - Required by SAP
- **Invoice Number** (BELNR) - Required by SAP

## ✅ Solutions Implemented

### 1. Enhanced Upload Endpoint
The SAP upload endpoint (`sap_upload_csv_view`) now automatically detects and handles both formats:

**Standard SAP Format:**
```csv
material_number,plant_code,vendor_id,vendor_name,purchase_date,invoice_number,fuel_type,quantity,unit,total_cost,cost_per_unit,currency,country,location_city,location_state
DIESEL-001,PLANT001,VEND001,Shell Oil,2023-10-22,FUEL00000001,Diesel,498.0365,liters,447.31,0.8981,USD,USA,Columbus,MN
```

**Logistics Format (Your Original):**
```csv
fuel_purchase_id,trip_id,truck_id,driver_id,purchase_date,location_city,location_state,gallons,price_per_gallon,total_cost,fuel_card_number
FUEL00000001,TRIP00051284,TRK00045,DRV00102,2023-10-22 05:00:00,Columbus,MN,131.6,3.399,447.31,FC567161
```

### 2. Automatic Field Mapping
When you upload your logistics format, the system automatically:

- **Maps `fuel_card_number` → `vendor_id`** using predefined vendor mappings
- **Generates `vendor_name`** based on fuel card (e.g., FC567161 → "Shell Oil")
- **Assigns `plant_code`** based on state location
- **Detects `fuel_type`** from price per gallon
- **Generates `material_number`** from fuel type
- **Converts gallons → liters** (SAP standard unit)
- **Calculates `cost_per_unit`** per liter
- **Sets `country`** to "USA" by default

## 🚀 How to Upload Your Data

### Option 1: Direct Upload (Recommended)
Simply upload your original `fuel_purchases.csv` file through the SAP dashboard upload interface. The system will automatically detect the format and transform the data.

**Steps:**
1. Go to SAP Procurement Dashboard
2. Click "Upload CSV"
3. Select `logistic data set/fuel_purchases.csv`
4. System will process and show results

### Option 2: Use Transformation Script
If you prefer to transform the data first, use the provided script:

```bash
python transform_fuel_data.py
```

This creates `fuel_purchases_sap_format.csv` which you can then upload.

### Option 3: Manual Preparation
Use the sample file as a template:
- Copy `logistic data set/fuel_purchases_sample_sap.csv`
- Fill in your data following the same format
- Upload the prepared file

## 📊 Vendor Mappings

The system uses these predefined vendor mappings (fuel card → vendor):

| Fuel Card | Vendor ID | Vendor Name |
|-----------|-----------|-------------|
| FC567161 | VEND001 | Shell Oil |
| FC717910 | VEND002 | Exxon Mobil |
| FC912816 | VEND003 | Chevron |
| FC776357 | VEND004 | BP America |
| FC391024 | VEND005 | Sunoco |
| FC277504 | VEND006 | ConocoPhillips |
| FC256663 | VEND007 | Valero |
| FC543608 | VEND008 | Marathon |
| FC484857 | VEND009 | Citgo |
| FC753360 | VEND010 | Tesoro |

**Note:** If your fuel cards aren't in this list, the system will generate vendor IDs automatically (e.g., FC123456 → VEND123456).

## 🏭 Plant Code Assignments

Plant codes are assigned based on state:

| State | Plant Code |
|-------|------------|
| TX, PA, TN, NV, AR, NE, ND, ME | PLANT001 |
| CA, OH, MI, VA, MN, KY, OR, WV, AK | PLANT002 |
| FL, GA, NC, MO, SC, MS, OK, RI, VT | PLANT003 |
| NY, IL, IN, AZ, MA, MD, CT, DE, WY | PLANT004 |
| IL, MI, WI, CO, LA, UT, NM, ID, NH, IA | PLANT005 |

States not listed will get a plant code based on row number.

## ⚠️ Validation Rules

The system performs these checks during upload:

### Errors (Will Block Upload)
- ❌ Missing plant code
- ❌ Invalid or missing purchase date
- ❌ Invalid quantity value
- ❌ Invalid cost value
- ❌ Unknown unit of measurement
- ❌ Duplicate invoice number

### Warnings (Will Flag for Review)
- ⚠️ Missing vendor ID
- ⚠️ Negative total cost
- ⚠️ Price spike detected (>$5.00 per liter)
- ⚠️ Abnormally high quantity (>10,000 liters)
- ⚠️ Suspicious vendor ID format (< 3 characters)

## 🔧 Customization Options

### Adding New Vendor Mappings
Edit `ingest/sap_views.py` and add to `LOGISTICS_VENDOR_MAP`:

```python
LOGISTICS_VENDOR_MAP = {
    # Add your mappings here
    'FC123456': {'id': 'VEND111', 'name': 'Your Vendor Name'},
}
```

### Modifying Plant Code Assignments
Edit `STATE_PLANT_MAP` in `ingest/sap_views.py`:

```python
STATE_PLANT_MAP = {
    'XX': 'PLANT006',  # Add your state mappings
}
```

### Adjusting Validation Thresholds
Edit these values in `sap_upload_csv_view`:

```python
price_spike_threshold = Decimal('5.0')  # $5 per liter
quantity_anomaly_threshold = Decimal('10000')  # 10000 liters
```

## 📈 Dashboard Features

After upload, you can:

1. **View Summary Statistics**
   - Total fuel spend
   - Total fuel quantity (in liters)
   - Number of vendors and plants
   - Pending approvals count

2. **Analyze Trends**
   - Monthly fuel spend trends
   - Plant-wise procurement costs
   - Vendor spend rankings
   - Fuel type distribution

3. **Monitor Issues**
   - Validation error breakdown
   - Price spike alerts
   - Duplicate invoice detection
   - Quantity anomaly warnings

4. **Manage Records**
   - Approve/reject records
   - Add notes to records
   - Lock records for audit
   - Export data to CSV

## 🛠️ Troubleshooting

### Upload Fails
**Problem:** "Missing plant code" error
**Solution:** Ensure all records have a valid state, or manually add plant codes to your data.

### Price Spike Warnings
**Problem:** Many records flagged for price spikes
**Solution:** Your data has prices >$5.00 per liter. This is normal for some fuel types. Review and approve if legitimate.

### Duplicate Invoice Errors
**Problem:** "Duplicate invoice number" errors
**Solution:** Check if you're uploading the same data twice. Each `fuel_purchase_id` must be unique.

### Data Transformation Issues
**Problem:** Script fails or produces incorrect output
**Solution:** 
1. Check that input file exists at `logistic data set/fuel_purchases.csv`
2. Ensure CSV format is correct (comma-separated, proper headers)
3. Review error messages for specific row issues

## 📝 File Locations

- **Original Data:** `logistic data set/fuel_purchases.csv`
- **Transformed Data:** `logistic data set/fuel_purchases_sap_format.csv` (after running script)
- **Sample SAP Format:** `logistic data set/fuel_purchases_sample_sap.csv`
- **Transformation Script:** `transform_fuel_data.py`
- **Upload Endpoint:** `ingest/sap_views.py` → `sap_upload_csv_view`

## 🎯 Quick Start Checklist

- [ ] Review your `fuel_purchases.csv` data
- [ ] Choose upload method (direct, script, or manual)
- [ ] If needed, customize vendor/plant mappings
- [ ] Upload file through SAP dashboard
- [ ] Review validation results
- [ ] Approve legitimate records
- [ ] Investigate any warnings/errors
- [ ] Check dashboard analytics

## 📞 Support

If you encounter issues:
1. Check the validation messages in the upload response
2. Review the `SAPValidationIssue` records in the database
3. Examine the raw data in `RawSAPRecord` table
4. Check server logs for detailed error messages

---

**Last Updated:** 2026-05-28  
**Version:** 1.0  
**Compatible with:** Django REST Framework, SQLite/PostgreSQL