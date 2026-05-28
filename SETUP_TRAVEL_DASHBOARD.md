# Travel Management Dashboard Setup Guide

This guide will help you set up the new Travel Management Dashboard module.

## Quick Setup

### 1. Backend Setup

```bash
# Install Python dependencies (if not already installed)
pip install djangorestframework django-cors-headers requests

# Run migrations
python manage.py migrate

# Create sample data for testing (optional)
python manage.py create_sample_travel_data

# Start the Django server
python manage.py runserver
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (including new recharts library)
npm install

# Start the development server
npm run dev
```

### 3. Access the Dashboard

After starting both servers:
- Main Dashboard: http://localhost:5173/
- Travel Dashboard: http://localhost:5173/travel-dashboard
- Bookings: http://localhost:5173/bookings
- Users: http://localhost:5173/users
- Import Logs: http://localhost:5173/import-logs

## Configuration

### Navan API Configuration

To enable Navan API integration:

1. Go to Django Admin: http://localhost:8000/admin/
2. Navigate to "Travel" → "Navan API Configurations"
3. Click "Add Navan API Configuration"
4. Enter your Navan API credentials:
   - Company ID
   - Client ID
   - Client Secret
5. Save the configuration

The system will automatically handle OAuth token refresh.

## Testing the Integration

### Test with Sample Data

Run the sample data command to populate the database with test data:

```bash
python manage.py create_sample_travel_data
```

This creates:
- 50 sample users
- 100 sample bookings (flights, hotels, cars, rail, black car)
- 20 sample import logs

### Test API Endpoints

You can test the API endpoints using curl or Postman:

```bash
# Get dashboard analytics
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/travel/dashboard/analytics/

# List bookings
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/travel/bookings/

# Sync users (requires admin)
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/travel/import/sync-users/
```

## Troubleshooting

### Database Migration Issues

If you encounter migration issues:

```bash
# Reset migrations (if needed)
python manage.py migrate travel zero
python manage.py migrate
```

### Frontend Dependencies

If frontend dependencies fail to install:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS Issues

If you encounter CORS errors, ensure your Django settings include:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

## Features Overview

### Dashboard Analytics
- Real-time metrics cards
- Monthly booking trends (bar chart)
- Booking status distribution (pie chart)
- Department-wise spend (horizontal bar chart)
- Region-wise bookings (bar chart)

### Booking Management
- Advanced search and filtering
- Sortable columns
- CSV export
- Policy compliance indicators
- Pagination

### User Sync
- One-click user synchronization
- Filter by department, region, policy level
- Active/inactive status tracking
- CSV export

### Import Logs
- Import operation monitoring
- Status tracking (success, failed, partial)
- Retry functionality
- Detailed error logging

## API Documentation

Full API documentation is available at:
- Swagger/ReDoc (if configured)
- `/api/travel/` endpoints

## Support

For issues or questions:
1. Check the main README.md
2. Review TRAVEL_DASHBOARD_README.md
3. Check Django logs for backend errors
4. Check browser console for frontend errors