from rest_framework import serializers
from travel.models import (
    NavanApiConfig, SyncedUser, Booking, FlightBooking, HotelBooking,
    CarBooking, RailBooking, BlackCarBooking, ImportLog
)


class NavanApiConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = NavanApiConfig
        fields = ['id', 'company_id', 'client_id', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['access_token', 'token_expires_at']


class SyncedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncedUser
        fields = '__all__'


class FlightBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightBooking
        fields = '__all__'


class HotelBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelBooking
        fields = '__all__'


class CarBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarBooking
        fields = '__all__'


class RailBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RailBooking
        fields = '__all__'


class BlackCarBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlackCarBooking
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    flight_details = FlightBookingSerializer(read_only=True)
    hotel_details = HotelBookingSerializer(read_only=True)
    car_details = CarBookingSerializer(read_only=True)
    rail_details = RailBookingSerializer(read_only=True)
    black_car_details = BlackCarBookingSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'


class BookingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing bookings"""
    booking_type_display = serializers.CharField(source='get_booking_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'booking_id', 'booking_type', 'booking_type_display',
            'confirmation_number', 'status', 'status_display', 'user_email',
            'user_name', 'booking_date', 'travel_date', 'amount', 'currency',
            'trip_name', 'is_out_of_policy', 'origin', 'destination', 'region',
            'created_at', 'updated_at'
        ]


class ImportLogSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    import_type_display = serializers.CharField(source='get_import_type_display', read_only=True)
    
    class Meta:
        model = ImportLog
        fields = '__all__'


class DashboardAnalyticsSerializer(serializers.Serializer):
    """Serializer for dashboard analytics data"""
    total_synced_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    total_trips = serializers.IntegerField()
    flights = serializers.IntegerField()
    hotels = serializers.IntegerField()
    rental_cars = serializers.IntegerField()
    rail_bookings = serializers.IntegerField()
    black_car_bookings = serializers.IntegerField()
    monthly_travel_spend = serializers.DecimalField(max_digits=12, decimal_places=2)
    out_of_policy_trips = serializers.IntegerField()


class MonthlyBookingTrendSerializer(serializers.Serializer):
    """Serializer for monthly booking trend data"""
    month = serializers.CharField()
    booking_count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)


class BookingStatusDistributionSerializer(serializers.Serializer):
    """Serializer for booking status distribution"""
    status = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class DepartmentSpendSerializer(serializers.Serializer):
    """Serializer for department-wise spend"""
    department = serializers.CharField()
    total_spend = serializers.DecimalField(max_digits=12, decimal_places=2)
    booking_count = serializers.IntegerField()


class RegionBookingsSerializer(serializers.Serializer):
    """Serializer for region-wise bookings"""
    region = serializers.CharField()
    booking_count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)