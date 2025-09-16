"""
URL configuration for TD Google Login package
"""
from django.urls import path
from . import views

app_name = 'td_google_login'

urlpatterns = [
    # OAuth flow endpoints
    path('login/', views.google_login, name='google_login'),
    path('callback/', views.google_callback, name='google_callback'),
    
    # API endpoints
    path('user-info/', views.google_user_info, name='google_user_info'),
    path('logout/', views.google_logout, name='google_logout'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
]
