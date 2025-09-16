"""
Views for TD Google Login package
"""
import json
import logging
from typing import Dict, Any

from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.contrib.auth import login as django_login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings

from . import settings as app_settings
from .utils import (
    GoogleOAuthHandler, 
    GoogleOAuthError, 
    create_or_update_user,
    verify_token_from_frontend,
    cache_user_info
)
from .signals import user_google_login

logger = logging.getLogger(__name__)


class GoogleLoginView(View):
    """
    Initiate Google OAuth login flow
    """
    
    def get(self, request, *args, **kwargs):
        """
        Redirect user to Google OAuth consent screen
        """
        try:
            handler = GoogleOAuthHandler()
            redirect_uri = request.GET.get('redirect_uri', app_settings.GOOGLE_REDIRECT_URI)
            auth_url, state = handler.generate_auth_url(redirect_uri)
            
            # Store state in session for additional security
            request.session[f"{app_settings.SESSION_KEY_PREFIX}oauth_state"] = state
            
            return HttpResponseRedirect(auth_url)
            
        except Exception as e:
            logger.error(f"Failed to initiate Google login: {e}")
            return JsonResponse({
                'error': 'Failed to initiate Google login',
                'message': str(e)
            }, status=500)


class GoogleCallbackView(View):
    """
    Handle Google OAuth callback
    """
    
    def get(self, request, *args, **kwargs):
        """
        Handle OAuth callback from Google (traditional flow)
        """
        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')
        
        if error:
            logger.error(f"Google OAuth error: {error}")
            return self._handle_error("Google OAuth authorization denied")
        
        if not code or not state:
            return self._handle_error("Missing authorization code or state")
        
        # Verify state matches session
        session_state = request.session.get(f"{app_settings.SESSION_KEY_PREFIX}oauth_state")
        if state != session_state:
            return self._handle_error("Invalid OAuth state")
        
        try:
            return self._process_oauth_flow(code, state, request)
        except GoogleOAuthError as e:
            logger.error(f"OAuth flow error: {e}")
            return self._handle_error(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in OAuth callback: {e}")
            return self._handle_error("An unexpected error occurred")
    
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        """
        Handle token verification from frontend (SPA flow)
        """
        try:
            data = json.loads(request.body)
            token = data.get('token') or data.get('credential')
            
            if not token:
                return JsonResponse({
                    'error': 'Missing token',
                    'success': False
                }, status=400)
            
            # Verify the ID token
            user_info = verify_token_from_frontend(token)
            
            # Create or update user
            user, created = create_or_update_user(user_info, {'access_token': token})
            
            # Log the user in
            django_login(request, user)
            
            # Send signal
            user_google_login.send(
                sender=self.__class__,
                user=user,
                user_info=user_info,
                created=created,
                request=request
            )
            
            # Cache user info
            cache_user_info(user.id, user_info)
            
            response_data = {
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'created': created,
                'redirect_url': app_settings.LOGIN_REDIRECT_URL
            }
            
            return JsonResponse(response_data)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data',
                'success': False
            }, status=400)
        except GoogleOAuthError as e:
            logger.error(f"Token verification error: {e}")
            return JsonResponse({
                'error': str(e),
                'success': False
            }, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in token verification: {e}")
            return JsonResponse({
                'error': 'An unexpected error occurred',
                'success': False
            }, status=500)
    
    def _process_oauth_flow(self, code: str, state: str, request):
        """
        Process the OAuth flow with authorization code
        """
        handler = GoogleOAuthHandler()
        
        # Exchange code for tokens
        token_info = handler.exchange_code_for_tokens(code, state)
        
        # Verify ID token and get user info
        id_token_str = token_info.get('id_token')
        if not id_token_str:
            raise GoogleOAuthError("Missing ID token in response")
        
        user_info = handler.verify_id_token(id_token_str)
        
        # Get additional user info if access token is available
        access_token = token_info.get('access_token')
        if access_token:
            try:
                additional_info = handler.get_user_info(access_token)
                user_info.update(additional_info)
            except GoogleOAuthError:
                # Don't fail if additional info retrieval fails
                pass
        
        # Create or update user
        user, created = create_or_update_user(user_info, token_info)
        
        # Log the user in
        django_login(request, user)
        
        # Send signal
        user_google_login.send(
            sender=self.__class__,
            user=user,
            user_info=user_info,
            created=created,
            request=request
        )
        
        # Cache user info
        cache_user_info(user.id, user_info)
        
        # Clean up session state
        if f"{app_settings.SESSION_KEY_PREFIX}oauth_state" in request.session:
            del request.session[f"{app_settings.SESSION_KEY_PREFIX}oauth_state"]
        
        # Redirect to success URL
        redirect_url = app_settings.FRONTEND_SUCCESS_URL or app_settings.LOGIN_REDIRECT_URL
        return HttpResponseRedirect(redirect_url)
    
    def _handle_error(self, error_message: str):
        """
        Handle OAuth errors
        """
        error_url = app_settings.FRONTEND_ERROR_URL
        if error_url:
            return HttpResponseRedirect(f"{error_url}?error={error_message}")
        
        return JsonResponse({
            'error': error_message,
            'success': False
        }, status=400)


@require_GET
def google_user_info(request):
    """
    Get current user's Google profile information
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'error': 'User not authenticated',
            'success': False
        }, status=401)
    
    try:
        profile = request.user.google_profile
        user_data = {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'google_profile': {
                'google_id': profile.google_id,
                'picture_url': profile.picture_url,
                'locale': profile.locale,
                'verified_email': profile.verified_email,
                'family_name': profile.family_name,
                'given_name': profile.given_name,
                'last_login_at': profile.last_login_at.isoformat() if profile.last_login_at else None,
            }
        }
        
        return JsonResponse({
            'success': True,
            'user': user_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching user info: {e}")
        return JsonResponse({
            'error': 'Failed to fetch user information',
            'success': False
        }, status=500)


@require_POST
@login_required
def google_logout(request):
    """
    Logout user and clear session
    """
    try:
        django_logout(request)
        
        return JsonResponse({
            'success': True,
            'message': 'Logged out successfully',
            'redirect_url': app_settings.LOGOUT_REDIRECT_URL
        })
        
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        return JsonResponse({
            'error': 'Failed to logout',
            'success': False
        }, status=500)


@require_GET
def health_check(request):
    """
    Health check endpoint for the Google login service
    """
    try:
        # Validate settings
        app_settings.validate_settings()
        
        return JsonResponse({
            'success': True,
            'status': 'healthy',
            'service': 'td-google-login',
            'version': '1.0.0'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)


# Function-based views for backwards compatibility
google_login = GoogleLoginView.as_view()
google_callback = GoogleCallbackView.as_view()
