import os
import requests
from typing import Dict, Any
from functools import lru_cache
import hashlib
import time
import json

class LicenseValidator:
    """Handle license validation with Supabase"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL', 'https://fnucalistftkegxiuhtn.supabase.co')
        self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY', 'your-anon-key')
        self.edge_function_url = f"{self.supabase_url}/functions/v1/validate_license"
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    @lru_cache(maxsize=128)
    def validate(self, license_key: str) -> Dict[str, Any]:
        """Validate license with caching"""
        # Check local cache first
        cache_key = hashlib.sha256(license_key.encode()).hexdigest()
        current_time = time.time()
        
        if cache_key in self._cache:
            cached, timestamp = self._cache[cache_key]
            if current_time - timestamp < self._cache_ttl:
                return cached
        
        # Special handling for development
        if license_key == 'community':
            result = {
                'valid': True,
                'tier': 'community',
                'remaining_calls': 1000
            }
            self._cache[cache_key] = (result, current_time)
            return result
        
        if license_key.startswith('test_'):
            # Test licenses for development
            tier = license_key.split('_')[1] if '_' in license_key else 'community'
            result = {
                'valid': True,
                'tier': tier if tier in ['community', 'professional', 'enterprise'] else 'community',
                'remaining_calls': None if tier != 'community' else 100
            }
            self._cache[cache_key] = (result, current_time)
            return result
        
        try:
            # Call Supabase Edge Function
            response = requests.post(
                self.edge_function_url,
                json={'license_key': license_key},
                headers={
                    'Authorization': f'Bearer {self.supabase_anon_key}',
                    'Content-Type': 'application/json'
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                # Cache successful validations
                if result.get('valid'):
                    self._cache[cache_key] = (result, current_time)
                return result
            else:
                return {'valid': False, 'error': f'HTTP {response.status_code}'}
                
        except requests.RequestException as e:
            # Fallback for network issues
            print(f"License validation failed: {e}")
            # Allow limited offline usage for known licenses
            if cache_key in self._cache:
                cached, _ = self._cache[cache_key]
                return cached
            return {'valid': False, 'error': str(e)}
    
    def track_usage(self, license_key: str, calls: int = 1) -> None:
        """Track usage asynchronously"""
        if license_key in ['community', 'test_community']:
            return  # Don't track local test licenses
        
        # Fire and forget - don't block on tracking
        try:
            requests.post(
                self.edge_function_url,
                json={'license_key': license_key, 'calls_to_add': calls},
                headers={'Authorization': f'Bearer {self.supabase_anon_key}'},
                timeout=1
            )
        except:
            pass  # Silent fail on tracking errors