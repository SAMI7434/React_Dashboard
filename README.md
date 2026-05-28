# Utility Bill Ingestion and Review

A Django REST + React application for ingesting utility electricity bill exports, normalizing messy data, flagging suspicious rows, and approving records before audit lock.

## Why the sample data looks realistic

Utility exports typically include meter identifiers, facility or service location, billing period start/end, usage values with a unit, tariff or rate plan, total charges, currency, and supplier name. This project mirrors those common fields and adds realistic quirks seen in utility portals:

- Mixed date formats (ISO, US, dot-delimited, and numeric).
- Billing periods that start mid-month and end mid-month.
- Units that vary between Wh, kWh, MWh, GWh, and BTU.
- Financial units that vary between Dollars, Thousand Dollars, and Million Dollars.
- Missing meter IDs, missing currency codes, and negative charges (credit adjustments).

The sample CSV in [sample-data/utility_bills_sample.csv](sample-data/utility_bills_sample.csv) includes these cases so the validation and normalization logic has something real to reason about.

## Backend setup (Django + DRF)

1. Create a virtual environment and install dependencies:

```
python -m venv venv
venv\Scripts\activate
pip install django djangorestframework django-cors-headers psycopg2-binary
```

2. Configure PostgreSQL connection (defaults shown below). Override as needed:

```
DB_NAME=utility_analytics
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

3. Run migrations and create an analyst user:

```
python manage.py migrate
python manage.py createsuperuser
python manage.py drf_create_token <username>
```

4. Start the server:

```
python manage.py runserver
```

## Frontend setup (React + Tailwind + Recharts)

1. Install dependencies:

```
cd frontend
npm install
```

2. Configure API base URL:

```
copy .env.example .env
```

3. Start the dev server:

```
npm run dev
```

## API documentation

See [docs/api.md](docs/api.md) for endpoints and sample payloads.

## Sample CSV

Upload [sample-data/utility_bills_sample.csv](sample-data/utility_bills_sample.csv) to see normalization and validation results.

## Key features

- CSV ingestion with normalization to MWh and Thousand Dollars
- Validation rules for missing meters, invalid dates, negative costs, and usage spikes
- Review workflow with approve/reject and audit lock
- Dashboard analytics with Recharts

## Notes

- Authentication uses DRF token auth (analyst role only).
- The UI is tailored for analysts reviewing and approving billing data.
