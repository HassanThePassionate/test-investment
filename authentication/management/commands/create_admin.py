from django.core.management.base import BaseCommand
from django.conf import settings
from authentication.models import AllUser
import os

class Command(BaseCommand):
    help = 'Creates the admin user from environment variables'

    def handle(self, *args, **options):
        # Check if admin already exists
        if AllUser.objects.filter(role='admin').exists():
            self.stdout.write(self.style.WARNING('Admin user already exists'))
            return

        # Get admin credentials from environment variables
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')
        admin_full_name = os.getenv('ADMIN_FULL_NAME')
        admin_location = os.getenv('ADMIN_LOCATION')
        admin_phone = os.getenv('ADMIN_PHONE')
        admin_occupation = os.getenv('ADMIN_OCCUPATION')

        # Validate required environment variables
        required_vars = {
            'ADMIN_EMAIL': admin_email,
            'ADMIN_PASSWORD': admin_password,
            'ADMIN_FULL_NAME': admin_full_name,
            'ADMIN_LOCATION': admin_location,
            'ADMIN_PHONE': admin_phone,
            'ADMIN_OCCUPATION': admin_occupation
        }

        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            self.stdout.write(
                self.style.ERROR(
                    f'Missing required environment variables: {", ".join(missing_vars)}'
                )
            )
            return

        try:
            # Create admin user
            admin = AllUser.objects.create_user(
                email=admin_email,
                password=admin_password,
                full_name=admin_full_name,
                location=admin_location,
                phone_number=admin_phone,
                occupation=admin_occupation,
                role='admin',
                status='active',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created admin user: {admin_email}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {str(e)}')
            ) 