# Utility Ingestion Architecture

## Flow overview

1. Analyst uploads a CSV export from a utility portal.
2. Raw rows are stored as `RawUtilityRecord` rows with the original values.
3. Normalization converts usage to MWh and cost to Thousand Dollars, with an audit log per conversion.
4. Validation rules add `ValidationIssue` rows for errors and warnings.
5. Analysts review normalized rows, approve, and lock for audit.

## Validation rules implemented

- Missing meter IDs
- Invalid or missing billing dates
- Billing end date before billing start date
- Missing usage values or unsupported units
- Missing total cost
- Negative cost
- Missing currency or supplier name
- Usage spikes greater than 3x previous cycle
- Unknown energy or cost units
- Extremely high normalized values
