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
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                -- Only create the table if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'sysadmin_notification'
                ) THEN
                    CREATE TABLE sysadmin_notification (
                        id BIGSERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        message TEXT NOT NULL,
                        notification_type VARCHAR(50) NOT NULL DEFAULT 'appointment_booked',
                        is_read BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        appointment_id BIGINT NULL,
                        counselor_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE
                    );
                    
                    CREATE INDEX sysadmin_notification_counselor_id_idx 
                    ON sysadmin_notification (counselor_id);
                    
                    CREATE INDEX sysadmin_notification_appointment_id_idx 
                    ON sysadmin_notification (appointment_id);
                    
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'public_appointment'
                    ) THEN
                        ALTER TABLE sysadmin_notification 
                        ADD CONSTRAINT sysadmin_notification_appointment_id_fkey 
                        FOREIGN KEY (appointment_id) 
                        REFERENCES public_appointment(id) 
                        ON DELETE CASCADE;
                    END IF;
                END IF;
            END $$;
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS sysadmin_notification CASCADE;
            """
        ),
    ]

