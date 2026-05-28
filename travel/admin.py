from django.contrib import admin
from travel.models import (
    NavanApiConfig, SyncedUser, Booking, FlightBooking, HotelBooking,
    CarBooking, RailBooking, BlackCarBooking, ImportLog
)


@admin.register(NavanApiConfig)
class NavanApiConfigAdmin(admin.ModelAdmin):
    list_display = ['company_id', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['company_id', 'client_id']
    readonly_fields = ['access_token', 'token_expires_at']


@admin.register(SyncedUser)
class SyncedUserAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'status', 'department', 'region', 'policy_level', 'last_sync_at']
    list_filter = ['status', 'department', 'region', 'policy_level']
    search_fields = ['email', 'first_name', 'last_name', 'full_name', 'employee_id']
    readonly_fields = ['navan_user_id', 'last_sync_at', 'created_at', 'updated_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_id', 'booking_type', 'user_name', 'status', 'amount', 
        'currency', 'booking_date', 'is_out_of_policy', 'region'
    ]
    list_filter = ['booking_type', 'status', 'is_out_of_policy', 'region']
    search_fields = ['booking_id', 'user_email', 'user_name', 'confirmation_number']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'booking_date'


@admin.register(FlightBooking)
class FlightBookingAdmin(admin.ModelAdmin):
    list_display = ['booking', 'airline', 'flight_number', 'departure_airport', 'arrival_airport', 'departure_time']
    list_filter = ['airline', 'cabin_class']
    search_fields = ['booking__booking_id', 'flight_number', 'passenger_name']


@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    list_display = ['booking', 'hotel_name', 'check_in_date', 'check_out_date', 'number_of_nights']
    list_filter = ['hotel_name']
    search_fields = ['booking__booking_id', 'hotel_name', 'guest_name']


@admin.register(CarBooking)
class CarBookingAdmin(admin.ModelAdmin):
    list_display = ['booking', 'car_company', 'car_type', 'pickup_datetime', 'dropoff_datetime']
    list_filter = ['car_company', 'car_type']
    search_fields = ['booking__booking_id', 'driver_name']


@admin.register(RailBooking)
class RailBookingAdmin(admin.ModelAdmin):
    list_display = ['booking', 'train_operator', 'train_number', 'departure_station', 'arrival_station', 'departure_time']
    list_filter = ['train_operator', 'cabin_class']
    search_fields = ['booking__booking_id', 'train_number', 'passenger_name']


@admin.register(BlackCarBooking)
class BlackCarBookingAdmin(admin.ModelAdmin):
    list_display = ['booking', 'service_provider', 'vehicle_type', 'pickup_datetime', 'passenger_name']
    list_filter = ['service_provider', 'vehicle_type']
    search_fields = ['booking__booking_id', 'passenger_name', 'flight_number']


@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = [
        'import_type', 'status', 'records_processed', 'records_created', 
        'records_failed', 'started_at', 'completed_at', 'duration_seconds'
    ]
    list_filter = ['import_type', 'status']
    search_fields = ['import_type', 'error_message']
    readonly_fields = ['created_at']
    date_hierarchy = 'started_at'