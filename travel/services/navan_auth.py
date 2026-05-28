import requests
from django.utils import timezone
from datetime import timedelta
from travel.models import NavanApiConfig


class NavanAuthService:
    """Service for handling Navan API authentication"""
    
    def __init__(self, company_id=None):
        """Initialize with company_id or use default config"""
        if company_id:
            self.config = NavanApiConfig.objects.get(company_id=company_id, is_active=True)
        else:
            self.config = NavanApiConfig.objects.filter(is_active=True).first()
            if not self.config:
                raise ValueError("No active Navan API configuration found")
    
    def get_access_token(self, force_refresh=False):
        """Get valid access token, refreshing if necessary"""
        if not force_refresh and self.config.is_token_valid():
            return self.config.access_token
        
        return self._refresh_token()
    
    def _refresh_token(self):
        """Refresh the access token from Navan API"""
        url = "https://api.navan.com/ta-auth/oauth/token"
        
        payload = {
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'grant_type': 'client_credentials'
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.post(url, data=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            access_token = data.get('access_token')
            expires_in = data.get('expires_in', 3600)  # Default 1 hour
            
            # Update config with new token
            self.config.access_token = access_token
            self.config.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
            self.config.save()
            
            return access_token
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to refresh Navan API token: {str(e)}")
    
    def get_authenticated_headers(self):
        """Get headers with authentication token"""
        token = self.get_access_token()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Navan-Company-Id': self.config.company_id
        }