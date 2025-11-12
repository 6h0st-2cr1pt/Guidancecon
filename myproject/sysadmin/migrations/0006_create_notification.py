# Generated migration to create Notification model
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('public', '0005_userprofile_college_appointment'),
        ('sysadmin', '0005_add_user_custom_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('notification_type', models.CharField(choices=[('appointment_booked', 'Appointment Booked'), ('appointment_cancelled', 'Appointment Cancelled'), ('appointment_confirmed', 'Appointment Confirmed'), ('appointment_rescheduled', 'Appointment Rescheduled'), ('appointment_reminder', 'Appointment Reminder'), ('system_update', 'System Update')], default='appointment_booked', max_length=50)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='public.appointment')),
                ('counselor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]

