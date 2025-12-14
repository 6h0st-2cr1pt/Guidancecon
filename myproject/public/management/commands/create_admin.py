"""
Management command to create a Django admin superuser.
Usage: python manage.py create_admin
This command is idempotent - it will create or update the admin user.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.contrib.auth.backends import ModelBackend

User = get_user_model()

# Try to import UserProfile, but don't fail if it doesn't exist
try:
    from public.models import UserProfile
    HAS_USERPROFILE = True
except ImportError:
    HAS_USERPROFILE = False


class Command(BaseCommand):
    help = 'Creates or updates a Django admin superuser with predefined credentials'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'jonaldsabordo@gmail.com'
        password = 'admin'

        try:
            # Check if user already exists
            try:
                user = User.objects.get(username=username)
                created = False
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                created = True
            
            # Ensure user has all required permissions for Django admin
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.set_password(password)  # Always reset password to ensure it's correct
            user.save()
            
            # Remove UserProfile if it exists (admin user shouldn't have one)
            # This prevents conflicts with StudentIDBackend
            if HAS_USERPROFILE:
                try:
                    profile = UserProfile.objects.get(user=user)
                    profile.delete()
                    self.stdout.write(
                        self.style.WARNING(f'Removed UserProfile for admin user to prevent authentication conflicts')
                    )
                except UserProfile.DoesNotExist:
                    pass  # No profile exists, which is correct
            
            # Verify the user can authenticate with ModelBackend (used by Django admin)
            backend = ModelBackend()
            test_user = backend.authenticate(
                request=None,
                username=username,
                password=password
            )
            
            if test_user and test_user.is_staff and test_user.is_superuser:
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Successfully created superuser "{username}" with email "{email}"'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Updated existing user "{username}" to superuser with email "{email}"'
                        )
                    )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ User verification: is_staff={user.is_staff}, is_superuser={user.is_superuser}, is_active={user.is_active}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ User created but authentication verification failed!'
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
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
            # Don't raise the exception - allow the server to start even if admin creation fails

