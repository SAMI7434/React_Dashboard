# Travel Management Dashboard

A comprehensive travel management module integrated with Navan TMC API, featuring booking management, user synchronization, analytics, and import monitoring.

## Features

### Dashboard Analytics
- **Real-time Metrics**: Total synced users, active users, total trips, monthly spend, out-of-policy trips
- **Booking Type Breakdown**: Flights, Hotels, Rental Cars, Rail, Black Car bookings
- **Interactive Charts**:
  - Monthly booking trend
  - Booking status distribution
  - Department-wise travel spend
  - Region-wise bookings
  - Booking type comparison

### Booking Management
- Advanced booking table with search, filters, pagination, and sorting
- Export bookings to CSV
- Status badges and policy compliance indicators
- Support for multiple booking types (Flight, Hotel, Car, Rail, Black Car)

### User Sync
- Sync users from Navan API
- Filter by department, region, policy level
- View active/inactive/pending users
- Export user data to CSV

### Import Monitoring
- Track all import operations (users, bookings, reconciliation)
- View import status, records processed, and errors
- Retry failed imports
- Detailed import logs with validation errors

## Setup

### Backend Setup

1. **Install Dependencies**
   ```bash
   pip install djangorestframework django-cors-headers requests
   ```

2. **Run Migrations**
   ```bash
   python manage.py makemigrations travel
   python manage.py migrate
   ```

3. **Create Sample Data (Optional)**
   ```bash
   python manage.py create_sample_travel_data
   ```

4. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure Environment**
   Create `.env` file:
   ```
   VITE_API_URL=http://localhost:8000/api
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```

## API Endpoints

### Dashboard Analytics
- `GET /api/travel/dashboard/analytics/` - Dashboard analytics data
- `GET /api/travel/dashboard/monthly-trend/` - Monthly booking trend
- `GET /api/travel/dashboard/status-distribution/` - Booking status distribution
- `GET /api/travel/dashboard/department-spend/` - Department-wise spend
- `GET /api/travel/dashboard/region-bookings/` - Region-wise bookings
- `GET /api/travel/dashboard/booking-type-comparison/` - Booking type comparison
- `GET /api/travel/dashboard/recent-imports/` - Recent import logs

### Bookings
- `GET /api/travel/bookings/` - List bookings (with filters, pagination, sorting)
- `GET /api/travel/bookings/{id}/` - Retrieve booking details
- `GET /api/travel/bookings/booking_types/` - List booking types
- `GET /api/travel/bookings/regions/` - List regions

### Users
- `GET /api/travel/users/` - List synced users (with filters, pagination)
- `GET /api/travel/users/{id}/` - Retrieve user details
- `POST /api/travel/import/sync-users/` - Trigger user sync
- `GET /api/travel/users/departments/` - List departments
- `GET /api/travel/users/regions/` - List regions

### Import Logs
- `GET /api/travel/import-logs/` - List import logs (with filters, pagination)
- `GET /api/travel/import-logs/{id}/` - Retrieve import log details
- `POST /api/travel/import/bookings/` - Trigger booking import
- `POST /api/travel/import/reconciliation/` - Trigger daily reconciliation

## Database Models

### NavanApiConfig
Configuration for Navan API integration including OAuth credentials.

### SyncedUser
User data synced from Navan API with department, region, and policy information.

### Booking
Main booking model supporting multiple booking types with policy compliance tracking.

### Type-Specific Models
- `FlightBooking` - Flight-specific details
- `HotelBooking` - Hotel-specific details
- `CarBooking` - Rental car-specific details
- `RailBooking` - Rail-specific details
- `BlackCarBooking` - Black car/chauffeur details

### ImportLog
Logs for all import operations with status, records processed, and error tracking.

## Navan API Integration

The system integrates with Navan TMC API for:
- OAuth authentication
- User synchronization
- Booking data retrieval
- Trip import

### Configuration
Set up Navan API credentials in Django admin:
1. Go to `/admin/travel/navanapiconfig/`
2. Add new configuration with company ID, client ID, and client secret
3. System will automatically handle OAuth token refresh

## Frontend Pages

### Travel Dashboard (`/travel-dashboard`)
Main analytics dashboard with charts and metrics.

### Bookings (`/bookings`)
Booking management with advanced filtering and export.

### Users (`/users`)
User synchronization and management.

### Import Logs (`/import-logs`)
Import operation monitoring and retry functionality.

## Constraints

- Existing dashboard functionality preserved
- No modifications to unrelated existing models
- Modular and scalable architecture
- Reuses existing authentication and layout

## Future Enhancements

- Celery integration for scheduled syncs
- Advanced reporting and analytics
- Email notifications for import failures
- Multi-company support
- Custom policy rules engine