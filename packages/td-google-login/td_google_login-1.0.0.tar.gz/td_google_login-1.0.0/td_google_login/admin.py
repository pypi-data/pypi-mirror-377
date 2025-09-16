"""
Admin configuration for TD Google Login package
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import GoogleUserProfile, GoogleOAuthState


@admin.register(GoogleUserProfile)
class GoogleUserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'google_id', 'verified_email', 'picture_thumbnail', 
        'last_login_at', 'created_at'
    ]
    list_filter = ['verified_email', 'locale', 'created_at', 'last_login_at']
    search_fields = ['user__username', 'user__email', 'google_id', 'given_name', 'family_name']
    readonly_fields = [
        'google_id', 'created_at', 'updated_at', 'last_login_at', 
        'picture_preview', 'token_status'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'google_id', 'verified_email')
        }),
        ('Profile Details', {
            'fields': ('given_name', 'family_name', 'picture_url', 'picture_preview', 'locale')
        }),
        ('Token Information', {
            'fields': ('token_status', 'token_expires_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_login_at'),
            'classes': ('collapse',)
        }),
    )
    
    def picture_thumbnail(self, obj):
        """Display a small thumbnail of the user's profile picture"""
        if obj.picture_url:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius: 50%;" />',
                obj.picture_url
            )
        return "No picture"
    picture_thumbnail.short_description = "Picture"
    
    def picture_preview(self, obj):
        """Display a larger preview of the user's profile picture"""
        if obj.picture_url:
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius: 10px;" />',
                obj.picture_url
            )
        return "No picture available"
    picture_preview.short_description = "Picture Preview"
    
    def token_status(self, obj):
        """Display token validity status"""
        if obj.is_token_valid():
            return format_html('<span style="color: green;">✓ Valid</span>')
        return format_html('<span style="color: red;">✗ Expired/Invalid</span>')
    token_status.short_description = "Token Status"


@admin.register(GoogleOAuthState)
class GoogleOAuthStateAdmin(admin.ModelAdmin):
    list_display = ['state_preview', 'redirect_uri', 'used', 'created_at']
    list_filter = ['used', 'created_at']
    search_fields = ['state', 'redirect_uri']
    readonly_fields = ['state', 'created_at']
    
    def state_preview(self, obj):
        """Show a preview of the state string"""
        return f"{obj.state[:20]}..." if len(obj.state) > 20 else obj.state
    state_preview.short_description = "State"
    
    def has_add_permission(self, request):
        """Disable manual creation of OAuth states"""
        return False
