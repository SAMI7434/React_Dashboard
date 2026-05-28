import requests
import logging
from django.utils import timezone
from travel.services.navan_auth import NavanAuthService
from travel.models import SyncedUser, ImportLog

logger = logging.getLogger(__name__)


class NavanUserService:
    """Service for syncing users from Navan API"""
    
    def __init__(self, company_id=None):
        self.auth_service = NavanAuthService(company_id)
    
    def sync_users(self):
        """Sync all users from Navan API"""
        import_log = ImportLog.objects.create(
            import_type='users',
            status='retry',
            started_at=timezone.now()
        )
        
        try:
            headers = self.auth_service.get_authenticated_headers()
            users_data = self._fetch_all_users(headers)
            
            records_created = 0
            records_updated = 0
            records_failed = 0
            
            for user_data in users_data:
                try:
                    self._process_user(user_data)
                    if user_data.get('created_at'):
                        records_created += 1
                    else:
                        records_updated += 1
                except Exception as e:
                    logger.error(f"Failed to process user {user_data.get('id')}: {str(e)}")
                    records_failed += 1
            
            import_log.records_processed = len(users_data)
            import_log.records_created = records_created
            import_log.records_updated = records_updated
            import_log.records_failed = records_failed
            import_log.status = 'success' if records_failed == 0 else 'partial'
            import_log.completed_at = timezone.now()
            import_log.save()
            
            return {
                'success': True,
                'records_processed': len(users_data),
                'records_created': records_created,
                'records_updated': records_updated,
                'records_failed': records_failed
            }
            
        except Exception as e:
            logger.error(f"User sync failed: {str(e)}")
            import_log.status = 'failed'
            import_log.error_message = str(e)
            import_log.completed_at = timezone.now()
            import_log.save()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _fetch_all_users(self, headers):
        """Fetch all users with pagination"""
        url = "https://api.navan.com/v1/users"
        all_users = []
        page_token = None
        
        while True:
            params = {'page_size': 100}
            if page_token:
                params['page_token'] = page_token
            
            response = requests.get(url, headers=headers, params=params, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            users = data.get('data', [])
            all_users.extend(users)
            
            page_token = data.get('next_page_token')
            if not page_token:
                break
        
        return all_users
    
    def _process_user(self, user_data):
        """Process and save/update a single user"""
        navan_user_id = user_data.get('id')
        
        defaults = {
            'email': user_data.get('work_email', ''),
            'first_name': user_data.get('first_name', ''),
            'last_name': user_data.get('last_name', ''),
            'full_name': user_data.get('display_name', ''),
            'status': 'active' if user_data.get('is_active', True) else 'inactive',
            'department': user_data.get('department', ''),
            'region': user_data.get('region', ''),
            'policy_level': user_data.get('policy_level', ''),
            'manager_id': user_data.get('manager_id', ''),
            'cost_center': user_data.get('cost_center', ''),
            'employee_id': user_data.get('employee_id', ''),
            'phone': user_data.get('phone', ''),
            'last_sync_at': timezone.now()
        }
        
        SyncedUser.objects.update_or_create(
            navan_user_id=navan_user_id,
            defaults=defaults
        )