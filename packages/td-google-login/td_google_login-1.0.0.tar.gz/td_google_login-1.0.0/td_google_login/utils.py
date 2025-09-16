"""
Utility functions for Google OAuth authentication
"""
import json
import secrets
import logging
from urllib.parse import urlencode, parse_qs, urlparse
from typing import Dict, Optional, Tuple

import requests
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone

from . import settings as app_settings
from .models import GoogleUserProfile, GoogleOAuthState

logger = logging.getLogger(__name__)


class GoogleOAuthError(Exception):
    """Custom exception for Google OAuth errors"""
    pass


class GoogleOAuthHandler:
    """
    Main handler for Google OAuth operations
    """
    
    def __init__(self):
        app_settings.validate_settings()
        self.client_id = app_settings.GOOGLE_CLIENT_ID
        self.client_secret = app_settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = app_settings.GOOGLE_REDIRECT_URI
        self.scopes = app_settings.GOOGLE_OAUTH_SCOPES
        
    def generate_auth_url(self, redirect_uri: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate Google OAuth authorization URL
        
        Returns:
            Tuple of (auth_url, state)
        """
        state = secrets.token_urlsafe(32)
        redirect_uri = redirect_uri or self.redirect_uri
        
        # Store state in database for security
        GoogleOAuthState.objects.create(
            state=state,
            redirect_uri=redirect_uri
        )
        
        # Clean up old states
        GoogleOAuthState.cleanup_expired()
        
        auth_params = {
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'scope': ' '.join(self.scopes),
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent',
        }
        
        auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(auth_params)}"
        return auth_url, state
    
    def exchange_code_for_tokens(self, code: str, state: str) -> Dict:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            code: Authorization code from Google
            state: OAuth state parameter
            
        Returns:
            Dict containing token information
        """
        # Verify state parameter
        try:
            oauth_state = GoogleOAuthState.objects.get(state=state, used=False)
            oauth_state.used = True
            oauth_state.save()
        except GoogleOAuthState.DoesNotExist:
            raise GoogleOAuthError("Invalid or expired OAuth state")
        
        token_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': oauth_state.redirect_uri,
        }
        
        try:
            response = requests.post(
                'https://oauth2.googleapis.com/token',
                data=token_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Token exchange failed: {e}")
            raise GoogleOAuthError(f"Failed to exchange code for tokens: {e}")
    
    def verify_id_token(self, id_token_str: str) -> Dict:
        """
        Verify Google ID token and extract user information
        
        Args:
            id_token_str: The ID token string
            
        Returns:
            Dict containing user information
        """
        try:
            request = google_requests.Request()
            id_info = id_token.verify_oauth2_token(
                id_token_str, 
                request, 
                self.client_id
            )
            
            if app_settings.VERIFY_TOKEN_EXPIRY:
                # Check if token is expired
                if id_info.get('exp', 0) < timezone.now().timestamp():
                    raise GoogleOAuthError("ID token has expired")
            
            return id_info
        except ValueError as e:
            logger.error(f"ID token verification failed: {e}")
            raise GoogleOAuthError(f"Invalid ID token: {e}")
    
    def get_user_info(self, access_token: str) -> Dict:
        """
        Get additional user information from Google API
        
        Args:
            access_token: Google access token
            
        Returns:
            Dict containing user information
        """
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get user info: {e}")
            raise GoogleOAuthError(f"Failed to get user information: {e}")


def create_or_update_user(user_info: Dict, token_info: Dict) -> Tuple[User, bool]:
    """
    Create or update Django user based on Google user information
    
    Args:
        user_info: User information from Google
        token_info: Token information from OAuth flow
        
    Returns:
        Tuple of (User instance, created_flag)
    """
    google_id = user_info.get('sub') or user_info.get('id')
    email = user_info.get('email')
    
    if not google_id or not email:
        raise GoogleOAuthError("Missing required user information (ID or email)")
    
    # Try to find existing user by Google ID first
    try:
        profile = GoogleUserProfile.objects.get(google_id=google_id)
        user = profile.user
        created = False
    except GoogleUserProfile.DoesNotExist:
        # Try to find by email if create unknown user is disabled
        if not app_settings.CREATE_UNKNOWN_USER:
            try:
                user = User.objects.get(email=email)
                created = False
            except User.DoesNotExist:
                raise GoogleOAuthError(
                    "User creation is disabled and no existing user found"
                )
        else:
            # Create new user
            try:
                user = User.objects.get(email=email)
                created = False
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=email,  # Use email as username
                    email=email,
                    first_name=user_info.get('given_name', ''),
                    last_name=user_info.get('family_name', ''),
                )
                created = True
        
        # Create Google profile
        profile = GoogleUserProfile.objects.create(
            user=user,
            google_id=google_id
        )
    
    # Update user information if enabled
    if app_settings.UPDATE_USER_INFO:
        user.first_name = user_info.get('given_name', user.first_name)
        user.last_name = user_info.get('family_name', user.last_name)
        user.email = email
        user.save()
    
    # Update Google profile information
    profile.picture_url = user_info.get('picture', profile.picture_url)
    profile.locale = user_info.get('locale', profile.locale)
    profile.verified_email = user_info.get('email_verified', profile.verified_email)
    profile.family_name = user_info.get('family_name', profile.family_name)
    profile.given_name = user_info.get('given_name', profile.given_name)
    
    # Update token information
    profile.access_token = token_info.get('access_token', '')
    profile.refresh_token = token_info.get('refresh_token', profile.refresh_token)
    
    if 'expires_in' in token_info:
        expires_in = int(token_info['expires_in'])
        profile.token_expires_at = timezone.now() + timezone.timedelta(seconds=expires_in)
    
    profile.update_last_login()
    profile.save()
    
    return user, created


def verify_token_from_frontend(token: str) -> Dict:
    """
    Verify ID token received from frontend
    
    Args:
        token: ID token from Google
        
    Returns:
        Dict containing user information
    """
    handler = GoogleOAuthHandler()
    return handler.verify_id_token(token)


def cache_user_info(user_id: int, info: Dict, timeout: int = None) -> None:
    """
    Cache user information for performance
    
    Args:
        user_id: User ID
        info: Information to cache
        timeout: Cache timeout in seconds
    """
    timeout = timeout or app_settings.TOKEN_CACHE_TIMEOUT
    cache_key = f"{app_settings.SESSION_KEY_PREFIX}user_info_{user_id}"
    cache.set(cache_key, info, timeout)


def get_cached_user_info(user_id: int) -> Optional[Dict]:
    """
    Get cached user information
    
    Args:
        user_id: User ID
        
    Returns:
        Cached information or None
    """
    cache_key = f"{app_settings.SESSION_KEY_PREFIX}user_info_{user_id}"
    return cache.get(cache_key)
