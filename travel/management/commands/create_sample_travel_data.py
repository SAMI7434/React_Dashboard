from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from travel.models import (
    SyncedUser, Booking, FlightBooking, HotelBooking, 
    CarBooking, RailBooking, BlackCarBooking, ImportLog
)


class Command(BaseCommand):
    help = 'Create sample travel data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample travel data...')
        
        # Create sample users
        departments = ['Engineering', 'Sales', 'Marketing', 'Finance', 'HR', 'Operations']
        regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America']
        policy_levels = ['standard', 'premium', 'executive']
        
        users = []
        for i in range(50):
            first_name = f'User{i}'
            last_name = f'Test{i}'
            user = SyncedUser.objects.get_or_create(
                navan_user_id=f'user_{i}',
                defaults={
                    'email': f'user{i}@example.com',
                    'first_name': first_name,
                    'last_name': last_name,
                    'full_name': f'{first_name} {last_name}',
                    'status': random.choice(['active', 'active', 'active', 'inactive']),
                    'department': random.choice(departments),
                    'region': random.choice(regions),
                    'policy_level': random.choice(policy_levels),
                    'employee_id': f'EMP{i:04d}',
                }
            )[0]
            users.append(user)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))
        
        # Create sample bookings
        booking_types = ['flight', 'hotel', 'car', 'rail', 'black_car']
        statuses = ['confirmed', 'completed', 'cancelled', 'pending']
        currencies = ['USD', 'EUR', 'GBP']
        
        airlines = ['United', 'Delta', 'American', 'Lufthansa', 'British Airways']
        hotel_chains = ['Marriott', 'Hilton', 'Hyatt', 'IHG', 'Accor']
        car_companies = ['Hertz', 'Enterprise', 'Avis', 'Budget', 'National']
        train_operators = ['Amtrak', 'Eurostar', 'Deutsche Bahn', 'SNCF']
        black_car_services = ['Uber Black', 'Lyft Lux', 'Careblack', 'Juniper']
        
        bookings_created = 0
        for i in range(100):
            booking_type = random.choice(booking_types)
            user = random.choice(users)
            booking_date = timezone.now() - timedelta(days=random.randint(1, 90))
            travel_date = booking_date.date() + timedelta(days=random.randint(1, 30))
            
            booking = Booking.objects.create(
                booking_id=f'BK{i:06d}',
                booking_type=booking_type,
                confirmation_number=f'CONF{i:08d}',
                status=random.choice(statuses),
                user_email=user.email,
                user_name=user.full_name,
                navan_user_id=user.navan_user_id,
                booking_date=booking_date,
                travel_date=travel_date,
                amount=Decimal(str(round(random.uniform(100, 2000), 2))),
                currency=random.choice(currencies),
                trip_name=f'Trip {i}',
                cost_center=f'COST{i:03d}',
                is_out_of_policy=random.choice([True, False, False, False, False]),
                region=user.region,
                origin=random.choice(['NYC', 'LAX', 'CHI', 'MIA', 'SFO']),
                destination=random.choice(['LON', 'PAR', 'TOK', 'SYD', 'BER']),
            )
            
            # Create type-specific details
            try:
                if booking_type == 'flight':
                    FlightBooking.objects.create(
                        booking=booking,
                        airline=random.choice(airlines),
                        flight_number=f'FL{random.randint(100, 999)}',
                        cabin_class=random.choice(['Economy', 'Business', 'First']),
                        departure_airport='JFK',
                        arrival_airport='LHR',
                        departure_time=booking_date + timedelta(hours=10),
                        arrival_time=booking_date + timedelta(hours=22),
                        passenger_name=user.full_name,
                    )
                elif booking_type == 'hotel':
                    HotelBooking.objects.create(
                        booking=booking,
                        hotel_name=random.choice(hotel_chains),
                        hotel_address='123 Hotel St, City',
                        check_in_date=travel_date,
                        check_out_date=travel_date + timedelta(days=random.randint(1, 5)),
                        room_type=random.choice(['Standard', 'Deluxe', 'Suite']),
                        number_of_nights=random.randint(1, 5),
                        number_of_rooms=1,
                        guest_name=user.full_name,
                    )
                elif booking_type == 'car':
                    CarBooking.objects.create(
                        booking=booking,
                        car_company=random.choice(car_companies),
                        car_type=random.choice(['Economy', 'Compact', 'Midsize', 'Full-size', 'Luxury']),
                        pickup_location='Airport Terminal',
                        dropoff_location='Downtown Office',
                        pickup_datetime=booking_date + timedelta(hours=12),
                        dropoff_datetime=booking_date + timedelta(days=3, hours=12),
                        driver_name=user.full_name,
                    )
                elif booking_type == 'rail':
                    RailBooking.objects.create(
                        booking=booking,
                        train_operator=random.choice(train_operators),
                        train_number=f'TR{random.randint(100, 999)}',
                        departure_station='Penn Station',
                        arrival_station='Union Station',
                        departure_time=booking_date + timedelta(hours=8),
                        arrival_time=booking_date + timedelta(hours=12),
                        passenger_name=user.full_name,
                        cabin_class=random.choice(['Standard', 'First Class']),
                    )
                elif booking_type == 'black_car':
                    BlackCarBooking.objects.create(
                        booking=booking,
                        service_provider=random.choice(black_car_services),
                        vehicle_type=random.choice(['Sedan', 'SUV', 'Van']),
                        pickup_location='Office Building',
                        dropoff_location='Airport Terminal',
                        pickup_datetime=booking_date + timedelta(hours=6),
                        passenger_name=user.full_name,
                        flight_number=f'FL{random.randint(100, 999)}',
                    )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating details for booking {booking.booking_id}: {e}'))
                booking.delete()
                continue
            
            bookings_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {bookings_created} bookings'))
        
        # Create sample import logs
        import_types = ['users', 'bookings', 'trips', 'reconciliation']
        import_statuses = ['success', 'failed', 'partial']
        
        for i in range(20):
            ImportLog.objects.create(
                import_type=random.choice(import_types),
                status=random.choice(import_statuses),
                records_processed=random.randint(10, 100),
                records_created=random.randint(5, 50),
                records_updated=random.randint(0, 20),
                records_failed=random.randint(0, 5),
                started_at=timezone.now() - timedelta(hours=random.randint(1, 168)),
                completed_at=timezone.now() - timedelta(hours=random.randint(1, 168)) + timedelta(minutes=random.randint(1, 30)),
            )
        
        self.stdout.write(self.style.SUCCESS('Sample import logs created'))
        self.stdout.write(self.style.SUCCESS('Sample travel data creation complete!'))