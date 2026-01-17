"""
Management command to list all users in the database.
Usage: python manage.py list_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Lists all users in the database with their permissions'

    def handle(self, *args, **options):
        users = User.objects.all().order_by('id')
        
        if not users.exists():
            self.stdout.write(self.style.WARNING('No users found in database'))
            return
        
        self.stdout.write('=' * 80)
        self.stdout.write('ALL USERS IN DATABASE')
        self.stdout.write('=' * 80)
        
        for user in users:
            self.stdout.write(f'\nUser ID: {user.id}')
            self.stdout.write(f'  Username: {user.username}')
            self.stdout.write(f'  Email: {user.email}')
            self.stdout.write(f'  First Name: {user.first_name}')
            self.stdout.write(f'  Last Name: {user.last_name}')
            self.stdout.write(f'  is_staff: {user.is_staff}')
            self.stdout.write(f'  is_superuser: {user.is_superuser}')
            self.stdout.write(f'  is_active: {user.is_active}')
            self.stdout.write(f'  Date Joined: {user.date_joined}')
            self.stdout.write('-' * 80)

