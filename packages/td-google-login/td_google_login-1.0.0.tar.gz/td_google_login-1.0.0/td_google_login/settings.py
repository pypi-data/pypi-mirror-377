"""
Configuration settings for TD Google Login package
"""
import os
from django.conf import settings


def get_setting(name, default=None):
    """
    Get a setting value from Django settings or environment variables
    """
    # First try to get from Django settings
    if hasattr(settings, name):
        return getattr(settings, name)
    
    # Then try environment variables
    env_value = os.getenv(name)
    if env_value is not None:
        return env_value
    
    return default


# Google OAuth Configuration
GOOGLE_CLIENT_ID = get_setting('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = get_setting('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = get_setting('GOOGLE_REDIRECT_URI')

# Default redirect URLs
LOGIN_REDIRECT_URL = get_setting('TDG_LOGIN_REDIRECT_URL', '/')
LOGOUT_REDIRECT_URL = get_setting('TDG_LOGOUT_REDIRECT_URL', '/')

# Session configuration
SESSION_KEY_PREFIX = get_setting('TDG_SESSION_KEY_PREFIX', 'tdg_')

# User creation settings
CREATE_UNKNOWN_USER = get_setting('TDG_CREATE_UNKNOWN_USER', True)
UPDATE_USER_INFO = get_setting('TDG_UPDATE_USER_INFO', True)

# Google API scopes
GOOGLE_OAUTH_SCOPES = get_setting('TDG_GOOGLE_OAUTH_SCOPES', [
    'openid',
    'email',
    'profile'
])

# Token verification settings
VERIFY_TOKEN_EXPIRY = get_setting('TDG_VERIFY_TOKEN_EXPIRY', True)
TOKEN_CACHE_TIMEOUT = get_setting('TDG_TOKEN_CACHE_TIMEOUT', 3600)  # 1 hour

# Frontend configuration
FRONTEND_SUCCESS_URL = get_setting('TDG_FRONTEND_SUCCESS_URL', None)
FRONTEND_ERROR_URL = get_setting('TDG_FRONTEND_ERROR_URL', None)


def validate_settings():
    """
    Validate required settings are present
    """
    required_settings = [
        ('GOOGLE_CLIENT_ID', GOOGLE_CLIENT_ID),
        ('GOOGLE_CLIENT_SECRET', GOOGLE_CLIENT_SECRET),
    ]
    
    missing_settings = []
    for setting_name, setting_value in required_settings:
        if not setting_value:
            missing_settings.append(setting_name)
    
    if missing_settings:
        raise ValueError(
            f"Missing required Google OAuth settings: {', '.join(missing_settings)}. "
            "Please set these in your Django settings or environment variables."
        )
