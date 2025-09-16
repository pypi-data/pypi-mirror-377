"""
Signals for TD Google Login package
"""
import django.dispatch

# Signal sent when a user successfully logs in via Google
user_google_login = django.dispatch.Signal()

# Signal sent when a new user is created via Google OAuth
user_google_created = django.dispatch.Signal()

# Signal sent when a user's Google profile is updated
user_google_updated = django.dispatch.Signal()
