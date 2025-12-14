"""
Management command to create a Django admin superuser.
Usage: python manage.py create_admin
This command is idempotent - it will create or update the admin user.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates or updates a Django admin superuser with predefined credentials'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'jonaldsabordo@gmail.com'
        password = 'admin'

        try:
            # Check if user already exists
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True
                }
            )
            
            if created:
                # New user created, set password
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created superuser "{username}" with email "{email}"'
                    )
                )
            else:
                # User exists, update to ensure it's a superuser with correct password
                user.email = email
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.set_password(password)  # Reset password to ensure it's correct
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated existing user "{username}" to superuser with email "{email}"'
                    )
                )
                
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'IntegrityError: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating/updating superuser: {str(e)}')
            )
            # Don't raise the exception - allow the server to start even if admin creation fails

