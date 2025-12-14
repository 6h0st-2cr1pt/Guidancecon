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
                self.stdout.write(f'Found existing user "{username}"')
            except User.DoesNotExist:
                # Create superuser directly using create_superuser
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                created = True
                self.stdout.write(f'Created new superuser "{username}"')
            
            # Always ensure user has all required permissions for Django admin
            # This handles cases where user exists but isn't a superuser
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            # Always reset password to ensure it's correct
            user.set_password(password)
            # Save with all fields to ensure everything is updated
            user.save()
            
            # Refresh from database to ensure we have the latest state
            user.refresh_from_db()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'User state: is_staff={user.is_staff}, is_superuser={user.is_superuser}, is_active={user.is_active}'
                )
            )
            
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
                        f'✓ Authentication test passed! User can login with username="{username}" and password="{password}"'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ User created but authentication verification failed!'
                    )
                )
                self.stdout.write(
                    self.style.ERROR(
                        f'  test_user={test_user}, is_staff={test_user.is_staff if test_user else None}, is_superuser={test_user.is_superuser if test_user else None}'
                    )
                )
                # Try to verify password directly
                if user.check_password(password):
                    self.stdout.write(self.style.SUCCESS('  ✓ Password check passed'))
                else:
                    self.stdout.write(self.style.ERROR('  ✗ Password check failed!'))
                
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

