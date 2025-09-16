"""
Tests for TD Google Login views
"""
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from td_google_login.models import GoogleUserProfile, GoogleOAuthState


class GoogleLoginViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.google_login_url = reverse('td_google_login:google_login')
        self.google_callback_url = reverse('td_google_login:google_callback')
        self.health_check_url = reverse('td_google_login:health_check')
        
    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get(self.health_check_url)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['service'], 'td-google-login')
        self.assertEqual(data['version'], '1.0.0')
    
    @patch('td_google_login.utils.GoogleOAuthHandler')
    def test_google_login_redirect(self, mock_handler):
        """Test Google login redirect"""
        mock_instance = mock_handler.return_value
        mock_instance.generate_auth_url.return_value = ('https://accounts.google.com/oauth', 'state123')
        
        response = self.client.get(self.google_login_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('https://accounts.google.com/oauth'))
    
    def test_google_callback_missing_code(self):
        """Test callback without authorization code"""
        response = self.client.get(self.google_callback_url)
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Missing authorization code', data['error'])
    
    def test_google_callback_invalid_state(self):
        """Test callback with invalid state"""
        response = self.client.get(self.google_callback_url, {
            'code': 'auth_code_123',
            'state': 'invalid_state'
        })
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Invalid OAuth state', data['error'])
    
    @patch('td_google_login.utils.verify_token_from_frontend')
    @patch('td_google_login.utils.create_or_update_user')
    def test_token_verification_success(self, mock_create_user, mock_verify_token):
        """Test successful token verification"""
        # Mock user creation
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        mock_create_user.return_value = (user, True)
        
        # Mock token verification
        mock_verify_token.return_value = {
            'sub': 'google_id_123',
            'email': 'test@example.com',
            'given_name': 'Test',
            'family_name': 'User',
        }
        
        response = self.client.post(
            self.google_callback_url,
            data=json.dumps({'token': 'valid_token'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['email'], 'test@example.com')
        self.assertTrue(data['created'])
    
    def test_token_verification_invalid_json(self):
        """Test token verification with invalid JSON"""
        response = self.client.post(
            self.google_callback_url,
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Invalid JSON data', data['error'])
    
    def test_token_verification_missing_token(self):
        """Test token verification without token"""
        response = self.client.post(
            self.google_callback_url,
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Missing token', data['error'])
    
    def test_user_info_unauthenticated(self):
        """Test user info endpoint without authentication"""
        user_info_url = reverse('td_google_login:google_user_info')
        response = self.client.get(user_info_url)
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('User not authenticated', data['error'])
    
    def test_user_info_authenticated(self):
        """Test user info endpoint with authentication"""
        # Create user and profile
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        profile = GoogleUserProfile.objects.create(
            user=user,
            google_id='google_id_123',
            picture_url='https://example.com/picture.jpg',
            verified_email=True
        )
        
        # Login user
        self.client.force_login(user)
        
        user_info_url = reverse('td_google_login:google_user_info')
        response = self.client.get(user_info_url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['email'], 'test@example.com')
        self.assertEqual(data['user']['google_profile']['google_id'], 'google_id_123')
    
    def test_logout_authenticated(self):
        """Test logout endpoint"""
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com'
        )
        self.client.force_login(user)
        
        logout_url = reverse('td_google_login:google_logout')
        response = self.client.post(logout_url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('Logged out successfully', data['message'])
    
    def test_logout_unauthenticated(self):
        """Test logout endpoint without authentication"""
        logout_url = reverse('td_google_login:google_logout')
        response = self.client.post(logout_url)
        
        # Should redirect to login (302) or return 401
        self.assertIn(response.status_code, [302, 401])
