"""
Management command to clean up expired OAuth states
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from td_google_login.models import GoogleOAuthState


class Command(BaseCommand):
    help = 'Clean up expired OAuth state records'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=1,
            help='Age in hours for states to be considered expired (default: 1)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
    
    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']
        
        expiry_time = timezone.now() - timezone.timedelta(hours=hours)
        expired_states = GoogleOAuthState.objects.filter(created_at__lt=expiry_time)
        
        count = expired_states.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would delete {count} expired OAuth state records '
                    f'older than {hours} hours'
                )
            )
            for state in expired_states[:10]:  # Show first 10
                self.stdout.write(f'  - {state.state[:20]}... (created: {state.created_at})')
            if count > 10:
                self.stdout.write(f'  ... and {count - 10} more')
        else:
            expired_states.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {count} expired OAuth state records'
                )
            )
