"""
Models for TD Google Login package
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class GoogleUserProfile(models.Model):
    """
    Extended profile information for users authenticated via Google
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='google_profile'
    )
    google_id = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Google user ID"
    )
    picture_url = models.URLField(
        blank=True, 
        null=True,
        help_text="URL to user's Google profile picture"
    )
    locale = models.CharField(
        max_length=10, 
        blank=True, 
        null=True,
        help_text="User's locale preference"
    )
    verified_email = models.BooleanField(
        default=False,
        help_text="Whether the email is verified by Google"
    )
    family_name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="User's family name from Google"
    )
    given_name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="User's given name from Google"
    )
    
    # Token information
    access_token = models.TextField(
        blank=True, 
        null=True,
        help_text="Google access token (encrypted)"
    )
    refresh_token = models.TextField(
        blank=True, 
        null=True,
        help_text="Google refresh token (encrypted)"
    )
    token_expires_at = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="When the access token expires"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Last time user logged in via Google"
    )
    
    class Meta:
        verbose_name = "Google User Profile"
        verbose_name_plural = "Google User Profiles"
        
    def __str__(self):
        return f"{self.user.username} - Google Profile"
    
    def is_token_valid(self):
        """
        Check if the access token is still valid
        """
        if not self.token_expires_at:
            return False
        return timezone.now() < self.token_expires_at
    
    def update_last_login(self):
        """
        Update the last login timestamp
        """
        self.last_login_at = timezone.now()
        self.save(update_fields=['last_login_at'])


class GoogleOAuthState(models.Model):
    """
    Store OAuth state parameters for security
    """
    state = models.CharField(
        max_length=255, 
        unique=True,
        help_text="OAuth state parameter"
    )
    redirect_uri = models.URLField(
        help_text="Redirect URI for this OAuth flow"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Google OAuth State"
        verbose_name_plural = "Google OAuth States"
        
    def __str__(self):
        return f"OAuth State: {self.state[:20]}..."
    
    @classmethod
    def cleanup_expired(cls, hours=1):
        """
        Clean up expired state records
        """
        expiry_time = timezone.now() - timezone.timedelta(hours=hours)
        cls.objects.filter(created_at__lt=expiry_time).delete()
