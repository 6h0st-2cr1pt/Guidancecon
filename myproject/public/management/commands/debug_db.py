from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from public.models import UserProfile
from django.db import connection

class Command(BaseCommand):
    help = 'Debug database setup and create test user'

    def handle(self, *args, **options):
        # Check if tables exist
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'public_userprofile'
                );
            """)
            profile_table_exists = cursor.fetchone()[0]

            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'auth_user'
                );
            """)
            user_table_exists = cursor.fetchone()[0]

        self.stdout.write(f"User table exists: {user_table_exists}")
        self.stdout.write(f"UserProfile table exists: {profile_table_exists}")

        # Create test user
        test_student_id = "TEST001"
        test_password = "test12345"

        # Delete test user if exists
        User.objects.filter(username=test_student_id).delete()
        UserProfile.objects.filter(student_id=test_student_id).delete()

        try:
            # Create new test user
            user = User.objects.create_user(
                username=test_student_id,
                password=test_password,
                email='test@example.com',
                first_name='Test',
                last_name='User'
            )
            self.stdout.write(f"Created test user: {user}")

            # Create profile
            profile = UserProfile.objects.create(
                user=user,
                student_id=test_student_id,
                course='TEST COURSE',
                year_level='1st'
            )
            self.stdout.write(f"Created test profile: {profile}")

            self.stdout.write(self.style.SUCCESS(
                f'\nTest user created successfully!\n'
                f'Student ID: {test_student_id}\n'
                f'Password: {test_password}\n'
                f'\nTry logging in with these credentials.'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))