# Data Sources

## Source 1: Utility Billing Data (CSV)

### Format
- EIA-861 forms, utility company exports, ENERGY STAR Portfolio Manager
- CSV with varying column names and date formats

### Sample Structure
```csv
meter_id,facility_name,billing_start_date,billing_end_date,usage_value,usage_unit,total_cost,cost_unit,currency,supplier_name
MTR-001,Downtown Office,2024-01-01,2024-01-31,15000,kWh,1875.00,dollars,USD,City Power
```

### Production Limitations
- PDF bills require OCR/manual entry
- Complex rate structures (TOU, demand charges) not supported
- No support for estimated readings or billing adjustments

## Source 2: Navan Travel API

### Format
- RESTful API with OAuth 2.0
- Users, trips, bookings, expenses

### Production Limitations
- API version changes require updates
- Rate limiting needs graceful handling
- Large data volumes need incremental sync

## Source 3: SAP Fuel Data (CSV)

### Format
- SAP output formats (ALV, CSV)
- Fuel card transactions with date, fuel type, gallons, cost

### Sample Structure
```csv
card_number,transaction_date,fuel_type,gallons,price_per_gallon,total_amount,vehicle_id,location
FC-12345,2024-01-15,Diesel,45.67,3.89,177.66,TRK-001,Shell Station #123
```

### Production Limitations
- Different SAP versions output different formats
- No real-time integration (IDoc/BAPI)
- No currency conversion for international fleets