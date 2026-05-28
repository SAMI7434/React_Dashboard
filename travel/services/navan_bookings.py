import requests
import logging
from django.db import transaction
from django.utils import timezone
from travel.services.navan_auth import NavanAuthService
from travel.models import Booking, FlightBooking, HotelBooking, CarBooking, RailBooking, BlackCarBooking

logger = logging.getLogger(__name__)


class NavanBookingService:
    """Service for fetching and managing bookings from Navan API"""
    
    def __init__(self, company_id=None):
        self.auth_service = NavanAuthService(company_id)
    
    def fetch_bookings(self, start_date=None, end_date=None, booking_type=None):
        """Fetch bookings from Navan API"""
        headers = self.auth_service.get_authenticated_headers()
        url = "https://api.navan.com/v1/bookings"
        
        params = {}
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
        if booking_type:
            params['booking_type'] = booking_type
        
        all_bookings = []
        page_token = None
        
        while True:
            if page_token:
                params['page_token'] = page_token
            
            response = requests.get(url, headers=headers, params=params, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            bookings = data.get('data', [])
            all_bookings.extend(bookings)
            
            page_token = data.get('next_page_token')
            if not page_token:
                break
        
        return all_bookings
    
    @transaction.atomic
    def process_booking(self, booking_data):
        """Process and save a single booking"""
        booking_id = booking_data.get('id')
        
        # Check for duplicate
        if Booking.objects.filter(booking_id=booking_id).exists():
            return None
        
        # Determine booking type
        booking_type_map = {
            'flight': 'flight',
            'hotel': 'hotel',
            'car': 'car',
            'rail': 'rail',
            'black_car': 'black_car'
        }
        
        raw_type = booking_data.get('type', '').lower()
        booking_type = booking_type_map.get(raw_type)
        
        if not booking_type:
            logger.warning(f"Unknown booking type: {raw_type}")
            return None
        
        # Create main booking record
        booking = Booking.objects.create(
            booking_id=booking_id,
            booking_type=booking_type,
            confirmation_number=booking_data.get('confirmation_number'),
            status=self._map_status(booking_data.get('status')),
            user_email=booking_data.get('user_email', ''),
            user_name=booking_data.get('user_name', ''),
            navan_user_id=booking_data.get('user_id', ''),
            booking_date=booking_data.get('booked_at'),
            travel_date=booking_data.get('travel_date'),
            amount=booking_data.get('amount', 0),
            currency=booking_data.get('currency', 'USD'),
            trip_id=booking_data.get('trip_id'),
            trip_name=booking_data.get('trip_name'),
            cost_center=booking_data.get('cost_center'),
            is_out_of_policy=booking_data.get('is_out_of_policy', False),
            policy_violation_reason=booking_data.get('policy_violation_reason'),
            origin=booking_data.get('origin'),
            destination=booking_data.get('destination'),
            region=booking_data.get('region'),
            raw_data=booking_data
        )
        
        # Create type-specific details
        self._create_booking_details(booking, booking_type, booking_data)
        
        return booking
    
    def _map_status(self, api_status):
        """Map API status to internal status"""
        status_map = {
            'confirmed': 'confirmed',
            'cancelled': 'cancelled',
            'pending': 'pending',
            'completed': 'completed',
            'refunded': 'refunded'
        }
        return status_map.get(api_status, 'confirmed')
    
    def _create_booking_details(self, booking, booking_type, booking_data):
        """Create type-specific booking details"""
        try:
            if booking_type == 'flight':
                flight_data = booking_data.get('flight', {})
                FlightBooking.objects.create(
                    booking=booking,
                    airline=flight_data.get('airline'),
                    flight_number=flight_data.get('flight_number'),
                    cabin_class=flight_data.get('cabin_class'),
                    departure_airport=flight_data.get('departure_airport'),
                    arrival_airport=flight_data.get('arrival_airport'),
                    departure_time=flight_data.get('departure_time'),
                    arrival_time=flight_data.get('arrival_time'),
                    passenger_name=flight_data.get('passenger_name'),
                    seat_number=flight_data.get('seat_number')
                )
            elif booking_type == 'hotel':
                hotel_data = booking_data.get('hotel', {})
                HotelBooking.objects.create(
                    booking=booking,
                    hotel_name=hotel_data.get('hotel_name'),
                    hotel_address=hotel_data.get('hotel_address'),
                    check_in_date=hotel_data.get('check_in_date'),
                    check_out_date=hotel_data.get('check_out_date'),
                    room_type=hotel_data.get('room_type'),
                    number_of_nights=hotel_data.get('number_of_nights', 1),
                    number_of_rooms=hotel_data.get('number_of_rooms', 1),
                    guest_name=hotel_data.get('guest_name')
                )
            elif booking_type == 'car':
                car_data = booking_data.get('car', {})
                CarBooking.objects.create(
                    booking=booking,
                    car_company=car_data.get('car_company'),
                    car_type=car_data.get('car_type'),
                    pickup_location=car_data.get('pickup_location'),
                    dropoff_location=car_data.get('dropoff_location'),
                    pickup_datetime=car_data.get('pickup_datetime'),
                    dropoff_datetime=car_data.get('dropoff_datetime'),
                    driver_name=car_data.get('driver_name')
                )
            elif booking_type == 'rail':
                rail_data = booking_data.get('rail', {})
                RailBooking.objects.create(
                    booking=booking,
                    train_operator=rail_data.get('train_operator'),
                    train_number=rail_data.get('train_number'),
                    departure_station=rail_data.get('departure_station'),
                    arrival_station=rail_data.get('arrival_station'),
                    departure_time=rail_data.get('departure_time'),
                    arrival_time=rail_data.get('arrival_time'),
                    passenger_name=rail_data.get('passenger_name'),
                    seat_number=rail_data.get('seat_number'),
                    cabin_class=rail_data.get('cabin_class')
                )
            elif booking_type == 'black_car':
                black_car_data = booking_data.get('black_car', {})
                BlackCarBooking.objects.create(
                    booking=booking,
                    service_provider=black_car_data.get('service_provider'),
                    vehicle_type=black_car_data.get('vehicle_type'),
                    pickup_location=black_car_data.get('pickup_location'),
                    dropoff_location=black_car_data.get('dropoff_location'),
                    pickup_datetime=black_car_data.get('pickup_datetime'),
                    passenger_name=black_car_data.get('passenger_name'),
                    flight_number=black_car_data.get('flight_number')
                )
        except Exception as e:
            logger.error(f"Error creating booking details for {booking.booking_id}: {str(e)}")
            raise