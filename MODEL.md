# Data Model

## Core Entities

### ImportBatch
Tracks each file upload as a batch operation.
- `file_name`, `uploaded_by`, `upload_time`, `status`

### RawUtilityRecord
Stores original data exactly as received.
- `import_batch`, `row_number`, `meter_id`, `facility_name`
- `billing_start_date`, `billing_end_date`
- `usage_value`, `usage_unit`, `total_cost`, `cost_unit`
- `raw_row` (JSON - complete original row)

### NormalizedUtilityRecord
Source of truth with standardized units.
- Links to `RawUtilityRecord` for traceability
- Stores both original and normalized values
- `normalized_mwh`, `normalized_thousand_dollars`
- Workflow state: `status` (pending/approved/rejected), `locked`

### NormalizationLog
Audit trail of every unit conversion.
- `original_value`, `original_unit`, `normalized_value`, `normalized_unit`
- `conversion_formula`

### ValidationIssue
Tracks validation warnings and errors.
- `severity` (error/warning), `message`

## Key Design Decisions

1. **Multi-tenancy**: User-based isolation via `uploaded_by` on ImportBatch
2. **Audit Trail**: Raw records preserved, all transformations logged
3. **Unit Normalization**: Energy → MWh, Cost → Thousand Dollars
4. **Workflow**: Pending → Approved/Rejected with lock on approval