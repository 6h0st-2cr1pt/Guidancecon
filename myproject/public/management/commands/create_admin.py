"""
Management command to create a Django admin superuser.
Usage: python manage.py create_admin
This command is idempotent - it will skip creation if the user already exists.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates a Django admin superuser with predefined credentials'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'jonaldsabordo@gmail.com'
        password = 'admin'

        try:
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" already exists. Skipping creation.')
                )
                return

            # Create superuser
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created superuser "{username}" with email "{email}"'
                )
            )
        except IntegrityError as e:
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists (IntegrityError). Skipping creation.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            )
            # Don't raise the exception - allow the server to start even if admin creation fails

