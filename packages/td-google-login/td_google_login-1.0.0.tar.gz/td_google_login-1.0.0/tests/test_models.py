"""
Tests for TD Google Login models
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from td_google_login.models import GoogleUserProfile, GoogleOAuthState


class GoogleUserProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
    
    def test_create_google_profile(self):
        """Test creating a Google user profile"""
        profile = GoogleUserProfile.objects.create(
            user=self.user,
            google_id='google_id_123',
            picture_url='https://example.com/picture.jpg',
            verified_email=True,
            given_name='Test',
            family_name='User'
        )
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.google_id, 'google_id_123')
        self.assertTrue(profile.verified_email)
        self.assertEqual(str(profile), 'test@example.com - Google Profile')
    
    def test_token_validity_check(self):
        """Test token validity checking"""
        profile = GoogleUserProfile.objects.create(
            user=self.user,
            google_id='google_id_123'
        )
        
        # Token without expiry should be invalid
        self.assertFalse(profile.is_token_valid())
        
        # Future expiry should be valid
        future_time = timezone.now() + timedelta(hours=1)
        profile.token_expires_at = future_time
        profile.save()
        self.assertTrue(profile.is_token_valid())
        
        # Past expiry should be invalid
        past_time = timezone.now() - timedelta(hours=1)
        profile.token_expires_at = past_time
        profile.save()
        self.assertFalse(profile.is_token_valid())
    
    def test_update_last_login(self):
        """Test updating last login timestamp"""
        profile = GoogleUserProfile.objects.create(
            user=self.user,
            google_id='google_id_123'
        )
        
        # Initially no last login
        self.assertIsNone(profile.last_login_at)
        
        # Update last login
        profile.update_last_login()
        self.assertIsNotNone(profile.last_login_at)
        
        # Check it's recent
        time_diff = timezone.now() - profile.last_login_at
        self.assertLess(time_diff.total_seconds(), 60)  # Within last minute


class GoogleOAuthStateTestCase(TestCase):
    def test_create_oauth_state(self):
        """Test creating OAuth state record"""
        state = GoogleOAuthState.objects.create(
            state='random_state_123',
            redirect_uri='http://localhost:8000/callback/'
        )
        
        self.assertEqual(state.state, 'random_state_123')
        self.assertEqual(state.redirect_uri, 'http://localhost:8000/callback/')
        self.assertFalse(state.used)
        self.assertIsNotNone(state.created_at)
    
    def test_cleanup_expired_states(self):
        """Test cleanup of expired OAuth states"""
        # Create old state (2 hours ago)
        old_time = timezone.now() - timedelta(hours=2)
        old_state = GoogleOAuthState.objects.create(
            state='old_state',
            redirect_uri='http://localhost:8000/callback/'
        )
        old_state.created_at = old_time
        old_state.save()
        
        # Create recent state
        recent_state = GoogleOAuthState.objects.create(
            state='recent_state',
            redirect_uri='http://localhost:8000/callback/'
        )
        
        # Cleanup states older than 1 hour
        GoogleOAuthState.cleanup_expired(hours=1)
        
        # Old state should be deleted, recent state should remain
        self.assertFalse(GoogleOAuthState.objects.filter(state='old_state').exists())
        self.assertTrue(GoogleOAuthState.objects.filter(state='recent_state').exists())
    
    def test_oauth_state_string_representation(self):
        """Test string representation of OAuth state"""
        state = GoogleOAuthState.objects.create(
            state='very_long_state_string_that_should_be_truncated',
            redirect_uri='http://localhost:8000/callback/'
        )
        
        str_repr = str(state)
        self.assertTrue(str_repr.startswith('OAuth State: very_long_state_str'))
        self.assertTrue(str_repr.endswith('...'))
        self.assertLessEqual(len(str_repr), 30)  # Should be truncated
