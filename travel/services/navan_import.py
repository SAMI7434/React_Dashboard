import logging
from django.utils import timezone
from travel.services.navan_auth import NavanAuthService
from travel.services.navan_users import NavanUserService
from travel.services.navan_bookings import NavanBookingService
from travel.models import ImportLog, Booking

logger = logging.getLogger(__name__)


class NavanTripImportService:
    """Service for importing trips and managing import operations"""
    
    def __init__(self, company_id=None):
        self.auth_service = NavanAuthService(company_id)
        self.user_service = NavanUserService(company_id)
        self.booking_service = NavanBookingService(company_id)
    
    def import_trips(self, start_date=None, end_date=None):
        """Import trips from Navan API"""
        import_log = ImportLog.objects.create(
            import_type='trips',
            status='retry',
            started_at=timezone.now()
        )
        
        try:
            bookings_data = self.booking_service.fetch_bookings(start_date, end_date)
            
            records_created = 0
            records_failed = 0
            validation_errors = []
            
            for booking_data in bookings_data:
                try:
                    booking = self.booking_service.process_booking(booking_data)
                    if booking:
                        records_created += 1
                except Exception as e:
                    logger.error(f"Failed to import booking {booking_data.get('id')}: {str(e)}")
                    records_failed += 1
                    validation_errors.append({
                        'booking_id': booking_data.get('id'),
                        'error': str(e)
                    })
            
            import_log.records_processed = len(bookings_data)
            import_log.records_created = records_created
            import_log.records_failed = records_failed
            import_log.validation_errors = validation_errors
            import_log.status = 'success' if records_failed == 0 else 'partial'
            import_log.completed_at = timezone.now()
            import_log.save()
            
            return {
                'success': True,
                'records_processed': len(bookings_data),
                'records_created': records_created,
                'records_failed': records_failed,
                'validation_errors': validation_errors
            }
            
        except Exception as e:
            logger.error(f"Trip import failed: {str(e)}")
            import_log.status = 'failed'
            import_log.error_message = str(e)
            import_log.completed_at = timezone.now()
            import_log.save()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def daily_reconciliation(self):
        """Run daily reconciliation of bookings"""
        import_log = ImportLog.objects.create(
            import_type='reconciliation',
            status='retry',
            started_at=timezone.now()
        )
        
        try:
            # Get today's date and yesterday's date
            today = timezone.now().date()
            yesterday = today - timezone.timedelta(days=1)
            
            # Fetch bookings for yesterday
            bookings_data = self.booking_service.fetch_bookings(
                start_date=yesterday,
                end_date=today
            )
            
            # Check for duplicates and missing bookings
            duplicates = []
            new_bookings = []
            
            for booking_data in bookings_data:
                booking_id = booking_data.get('id')
                if Booking.objects.filter(booking_id=booking_id).exists():
                    duplicates.append(booking_id)
                else:
                    new_bookings.append(booking_data)
            
            # Import new bookings
            records_created = 0
            for booking_data in new_bookings:
                try:
                    self.booking_service.process_booking(booking_data)
                    records_created += 1
                except Exception as e:
                    logger.error(f"Reconciliation failed for booking {booking_data.get('id')}: {str(e)}")
            
            import_log.records_processed = len(bookings_data)
            import_log.records_created = records_created
            import_log.status = 'success'
            import_log.completed_at = timezone.now()
            import_log.save()
            
            return {
                'success': True,
                'total_bookings': len(bookings_data),
                'duplicates_found': len(duplicates),
                'new_bookings_imported': records_created
            }
            
        except Exception as e:
            logger.error(f"Daily reconciliation failed: {str(e)}")
            import_log.status = 'failed'
            import_log.error_message = str(e)
            import_log.completed_at = timezone.now()
            import_log.save()
            
            return {
                'success': False,
                'error': str(e)
            }