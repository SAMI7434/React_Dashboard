# API Documentation

Base URL: `http://localhost:8000/api`

## Authentication

### POST /auth/login/

Request:

```
{
  "username": "analyst",
  "password": "password"
}
```

Response:

```
{
  "token": "<token>",
  "user": {
    "id": 1,
    "username": "analyst",
    "first_name": "",
    "last_name": "",
    "email": ""
  }
}
```

### GET /auth/me/

Returns the authenticated user.

## CSV Upload

### POST /upload/

- Content-Type: `multipart/form-data`
- Field: `file`

Response:

```
{
  "batch": { "id": 4, "file_name": "utility.csv", "status": "completed" },
  "records_created": 30,
  "failed_records": 3,
  "suspicious_records": 4
}
```

## Dashboard

### GET /dashboard/

Response:

```
{
  "summary": {
    "total_thousand_dollars": "21.06",
    "total_mwh": "178.92",
    "uploaded_bills": 30,
    "failed_records": 3,
    "suspicious_records": 4
  },
  "normalization_quality": {
    "total_records": 30,
    "normalized_rows": 12,
    "failed_conversions": 3,
    "unknown_units": 2,
    "most_common_unit": "kWh",
    "success_rate": 90.0
  },
  "normalization_insights": [
    "12% of uploaded records required unit normalization.",
    "Industrial contained mixed energy units.",
    "3 records failed normalization due to unknown or missing units."
  ],
  "monthly_cost_trend": [
    { "month": "2026-01", "total_thousand_dollars": "3.30" }
  ],
  "monthly_usage_trend": [
    { "month": "2026-01", "usage_mwh": "31.20" }
  ],
  "tariff_breakdown": [
    { "tariff_type": "TOU-Industrial", "total_thousand_dollars": "8.74" }
  ],
  "recent_uploads": [
    { "id": 4, "file_name": "utility.csv", "status": "completed" }
  ]
}
```

## Records

### GET /records/

Query params:
- `status` (pending, approved, rejected)
- `meter_id` (partial match)

### POST /records/{id}/approve/

Approves and locks a record.

### POST /records/{id}/reject/

Rejects a record.

## Validation Issues

### GET /issues/

Lists validation issues with severity and message.

## Upload Batches

### GET /uploads/

Lists ingest batches and their counts.
