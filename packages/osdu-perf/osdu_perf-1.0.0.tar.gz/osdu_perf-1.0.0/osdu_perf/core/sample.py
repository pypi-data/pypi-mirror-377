import logging
import threading
import time
import os
import atexit
from azure.identity import ManagedIdentityCredential, AzureCliCredential
from azure.core.exceptions import ClientAuthenticationError

class Auth:
    _instance = None
    _lock = threading.Lock()
    _pid = None  # Track the process ID to handle forks
    
    def __new__(cls, client_id=None, scope="https://management.azure.com/", refresh_buffer_seconds=300):
        """
        Singleton pattern implementation with thread safety and fork handling.
        
        Args:
            client_id: Client ID for ManagedIdentityCredential (optional)
            scope: The scope for the token request
            refresh_buffer_seconds: Buffer time before expiration
        """
        current_pid = os.getpid()
        
        # Check if we're in a new process (after fork) or no instance exists
        if cls._instance is None or cls._pid != current_pid:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None or cls._pid != current_pid:
                    if cls._pid != current_pid:
                        logging.info(f"Process fork detected (PID {cls._pid} -> {current_pid}), resetting Auth singleton")
                    cls._instance = super(Auth, cls).__new__(cls)
                    cls._instance._initialized = False
                    cls._pid = current_pid
        
        return cls._instance
    
    @staticmethod
    def _is_running_locally():
        """Check if running locally (True) or in Azure cloud (False)."""
        is_local = os.environ.get('IS_LOCAL', '').lower()
        is_local_bool = is_local in ('true', '1', 'yes', 'on')
        return is_local_bool

    def __init__(self, client_id=None, scope="https://management.azure.com/", refresh_buffer_seconds=300):
        """
        Initialize Azure credential for authentication with token caching.
        
        Args:
            client_id: Client ID for ManagedIdentityCredential (optional)
            scope: The scope for the token request
            refresh_buffer_seconds: Buffer time before expiration
        """
        if self._initialized:
            return
        
        # Configure credential based on environment
        is_local = self._is_running_locally()
        if is_local:
            self.credential = AzureCliCredential()
            logging.info("Using Azure CLI credential (local environment)")
        else:
            self.credential = ManagedIdentityCredential(client_id=client_id) if client_id else ManagedIdentityCredential()
            logging.info(f"Using managed identity credential (Azure environment){f' with client_id: {client_id}' if client_id else ''}")
        
        self.scope = scope
        self.refresh_buffer_seconds = refresh_buffer_seconds
        
        # Initialize threading support with fallback
        try:
            self._token_lock = threading.RLock()
        except Exception:
            self._token_lock = None
            logging.warning("Threading unavailable, using non-threaded mode")
        
        # Initialize token cache and statistics
        self._cached_token = None
        self._token_expiry_time = 0
        self._total_token_requests = 0
        self._cache_hits = 0
        self._cache_misses = 0
        
        self._initialized = True
        atexit.register(self._cleanup)
        logging.info(f"Auth initialized (scope: {scope}, buffer: {refresh_buffer_seconds}s, PID: {os.getpid()})")

    def _cleanup(self):
        """Cleanup method called on process exit"""
        try:
            self._with_lock(lambda: setattr(self, '_cached_token', None) or setattr(self, '_token_expiry_time', 0))
        except Exception:
            pass  # Ignore cleanup errors

    def _with_lock(self, func):
        """Execute function with lock if available, otherwise without lock"""
        if self._token_lock:
            with self._token_lock:
                return func()
        else:
            return func()

    def get_auth_headers(self):
        """Get authorization headers with cached token"""
        token = self.get_bearer_token()
        return {
            "Authorization": f"Bearer {token}"
        }

    def get_bearer_token(self):
        """Get a bearer token with intelligent caching and automatic refresh."""
        return self._with_lock(lambda: self._get_token_internal(time.time()))
    
    def _get_token_internal(self, current_time):
        """Internal method to get token (called with or without lock)"""
        self._total_token_requests += 1
        
        # Check if we need to refresh the token
        if self._should_refresh_token(current_time):
            self._cache_misses += 1
            self._refresh_token()
            logging.debug(f"Token cache miss #{self._cache_misses}")
        else:
            self._cache_hits += 1
            logging.debug(f"Token cache hit #{self._cache_hits}")
        
        return self._cached_token

    def _should_refresh_token(self, current_time):
        """Check if token needs refreshing."""
        return (self._cached_token is None or 
                current_time >= (self._token_expiry_time - self.refresh_buffer_seconds))

    def _refresh_token(self):
        """Refresh the cached token from Azure credential"""
        try:
            token_response = self.credential.get_token(self.scope)
            self._cached_token = token_response.token
            self._token_expiry_time = token_response.expires_on
            
            expires_in_minutes = (token_response.expires_on - time.time()) / 60
            logging.info(f"Token refreshed, expires in {expires_in_minutes:.1f} minutes")
            
        except ClientAuthenticationError as e:
            logging.error(f"Authentication failed: {e}")
            self._cached_token = None
            self._token_expiry_time = 0
            raise
        except Exception as e:
            logging.error(f"Token refresh failed: {e}")
            self._cached_token = None
            self._token_expiry_time = 0
            raise

    def invalidate_cache(self):
        """Manually invalidate the token cache to force refresh on next request."""
        self._with_lock(lambda: setattr(self, '_cached_token', None) or setattr(self, '_token_expiry_time', 0))
        logging.info("Token cache invalidated")

    def is_token_valid(self):
        """Check if the current cached token is valid and not close to expiration."""
        if self._cached_token is None:
            return False
        return time.time() < (self._token_expiry_time - self.refresh_buffer_seconds)

    def get_token_info(self):
        """Get information about the current token for monitoring purposes."""
        return self._with_lock(self._get_token_info_internal)
    
    def _get_token_info_internal(self):
        """Internal method to get token info"""
        base_info = {
            "total_requests": self._total_token_requests,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": self._cache_hits / max(1, self._total_token_requests),
            "is_singleton": True,
            "pid": os.getpid()
        }
        
        if self._cached_token is None:
            return {**base_info, "status": "no_token", "expires_in_seconds": 0}
        
        expires_in_seconds = max(0, self._token_expiry_time - time.time())
        return {
            **base_info,
            "status": "cached" if self.is_token_valid() else "expired",
            "expires_in_seconds": expires_in_seconds,
            "scope": self.scope
        }

    @classmethod
    def get_instance(cls, client_id=None, scope="https://management.azure.com/", refresh_buffer_seconds=300):
        """Alternative way to get the singleton instance."""
        return cls(client_id, scope, refresh_buffer_seconds)

    @classmethod
    def reset_singleton(cls):
        """Reset the singleton instance. WARNING: Affects all users of the singleton!"""
        with cls._lock:
            if cls._instance:
                logging.warning("Resetting Auth singleton instance")
                try:
                    cls._instance._cleanup()
                except Exception:
                    pass
            cls._instance = None
            cls._pid = None

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    auth = Auth.get_instance(client_id="2f59abbc-7b40-4d0e-91b2-22ca3084bc84", scope="https://management.azure.com/.default")
    print(auth.get_bearer_token())
