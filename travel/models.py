from django.db import models
from django.utils import timezone
from datetime import timedelta


class NavanApiConfig(models.Model):
    """Configuration for Navan API integration"""
    company_id = models.CharField(max_length=100, unique=True)
    client_id = models.CharField(max_length=200)
    client_secret = models.CharField(max_length=200)
    access_token = models.TextField(blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Navan API Configuration"
        verbose_name_plural = "Navan API Configurations"

    def __str__(self):
        return self.company_id

    def is_token_valid(self):
        """Check if the current access token is still valid"""
        if not self.token_expires_at:
            return False
        # Add 5 minute buffer
        return timezone.now() < (self.token_expires_at - timedelta(minutes=5))


class SyncedUser(models.Model):
    """User synced from Navan API"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ]

    navan_user_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    department = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    policy_level = models.CharField(max_length=100, blank=True, null=True)
    manager_id = models.CharField(max_length=100, blank=True, null=True)
    cost_center = models.CharField(max_length=100, blank=True, null=True)
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    last_sync_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Synced User"
        verbose_name_plural = "Synced Users"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Booking(models.Model):
    """Main booking model for all booking types"""
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
    ]

    BOOKING_TYPE_CHOICES = [
        ('flight', 'Flight'),
        ('hotel', 'Hotel'),
        ('car', 'Rental Car'),
        ('rail', 'Rail'),
        ('black_car', 'Black Car'),
    ]

    booking_id = models.CharField(max_length=100, unique=True)
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPE_CHOICES)
    confirmation_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    
    # User information
    user_email = models.EmailField()
    user_name = models.CharField(max_length=200)
    navan_user_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Booking details
    booking_date = models.DateTimeField()
    travel_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Trip information
    trip_id = models.CharField(max_length=100, blank=True, null=True)
    trip_name = models.CharField(max_length=200, blank=True, null=True)
    cost_center = models.CharField(max_length=100, blank=True, null=True)
    
    # Policy compliance
    is_out_of_policy = models.BooleanField(default=False)
    policy_violation_reason = models.TextField(blank=True, null=True)
    
    # Location information
    origin = models.CharField(max_length=100, blank=True, null=True)
    destination = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional data
    raw_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ['-booking_date']

    def __str__(self):
        return f"{self.booking_type.title()} - {self.booking_id}"


class FlightBooking(models.Model):
    """Flight-specific booking details"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='flight_details')
    airline = models.CharField(max_length=100)
    flight_number = models.CharField(max_length=20)
    cabin_class = models.CharField(max_length=50, blank=True, null=True)
    departure_airport = models.CharField(max_length=10)
    arrival_airport = models.CharField(max_length=10)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    passenger_name = models.CharField(max_length=200)
    seat_number = models.CharField(max_length=10, blank=True, null=True)
    
    class Meta:
        verbose_name = "Flight Booking"
        verbose_name_plural = "Flight Bookings"


class HotelBooking(models.Model):
    """Hotel-specific booking details"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='hotel_details')
    hotel_name = models.CharField(max_length=200)
    hotel_address = models.TextField()
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    room_type = models.CharField(max_length=100, blank=True, null=True)
    number_of_nights = models.IntegerField(default=1)
    number_of_rooms = models.IntegerField(default=1)
    guest_name = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = "Hotel Booking"
        verbose_name_plural = "Hotel Bookings"


class CarBooking(models.Model):
    """Rental car-specific booking details"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='car_details')
    car_company = models.CharField(max_length=100)
    car_type = models.CharField(max_length=100)
    pickup_location = models.CharField(max_length=200)
    dropoff_location = models.CharField(max_length=200)
    pickup_datetime = models.DateTimeField()
    dropoff_datetime = models.DateTimeField()
    driver_name = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = "Car Booking"
        verbose_name_plural = "Car Bookings"


class RailBooking(models.Model):
    """Rail-specific booking details"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='rail_details')
    train_operator = models.CharField(max_length=100)
    train_number = models.CharField(max_length=20)
    departure_station = models.CharField(max_length=100)
    arrival_station = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    passenger_name = models.CharField(max_length=200)
    seat_number = models.CharField(max_length=10, blank=True, null=True)
    cabin_class = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = "Rail Booking"
        verbose_name_plural = "Rail Bookings"


class BlackCarBooking(models.Model):
    """Black car/chauffeur-specific booking details"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='black_car_details')
    service_provider = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=100)
    pickup_location = models.CharField(max_length=200)
    dropoff_location = models.CharField(max_length=200)
    pickup_datetime = models.DateTimeField()
    passenger_name = models.CharField(max_length=200)
    flight_number = models.CharField(max_length=20, blank=True, null=True)  # For airport pickups
    
    class Meta:
        verbose_name = "Black Car Booking"
        verbose_name_plural = "Black Car Bookings"


class ImportLog(models.Model):
    """Log entries for data import operations"""
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('partial', 'Partial Success'),
        ('retry', 'Retry'),
    ]

    IMPORT_TYPE_CHOICES = [
        ('users', 'User Sync'),
        ('bookings', 'Booking Import'),
        ('trips', 'Trip Import'),
        ('reconciliation', 'Daily Reconciliation'),
    ]

    import_type = models.CharField(max_length=30, choices=IMPORT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    records_processed = models.IntegerField(default=0)
    records_created = models.IntegerField(default=0)
    records_updated = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    
    error_message = models.TextField(blank=True, null=True)
    validation_errors = models.JSONField(default=list, blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.FloatField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Import Log"
        verbose_name_plural = "Import Logs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.import_type} - {self.status} - {self.started_at}"

    def save(self, *args, **kwargs):
        if self.started_at and self.completed_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        super().save(*args, **kwargs)