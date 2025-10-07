"""Create Timeslot model

Generated manually to add Timeslot model which stores availability booleans.
"""
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sysadmin', '0002_counselor_timeslot_delete_customuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='Timeslot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('available', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timeslots', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('date', 'start_time'),
                'unique_together': {('user', 'date', 'start_time')},
            },
        ),
    ]
