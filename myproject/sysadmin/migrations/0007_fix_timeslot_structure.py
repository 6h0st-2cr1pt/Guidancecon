# Migration to fix sysadmin_timeslot table structure
# The table exists but may have wrong column structure from migration 0003 being faked
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sysadmin', '0006_create_notification'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                -- Check if table exists but doesn't have user_id column
                IF EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'sysadmin_timeslot'
                ) AND NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'sysadmin_timeslot' 
                    AND column_name = 'user_id'
                ) THEN
                    -- Table exists but missing user_id, need to fix it
                    -- First, check if it has counselor_id (old structure)
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'sysadmin_timeslot' 
                        AND column_name = 'counselor_id'
                    ) THEN
                        -- Old structure: drop the table and recreate
                        DROP TABLE IF EXISTS sysadmin_timeslot CASCADE;
                    ELSE
                        -- Table exists but structure is wrong, drop it
                        DROP TABLE IF EXISTS sysadmin_timeslot CASCADE;
                    END IF;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        # Now recreate the table with correct structure
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                -- Only create if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'sysadmin_timeslot'
                ) THEN
                    CREATE TABLE sysadmin_timeslot (
                        id BIGSERIAL PRIMARY KEY,
                        date DATE NOT NULL,
                        start_time TIME NOT NULL,
                        available BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE
                    );
                    
                    CREATE UNIQUE INDEX sysadmin_timeslot_user_date_start_time_uniq 
                    ON sysadmin_timeslot (user_id, date, start_time);
                    
                    CREATE INDEX sysadmin_timeslot_user_id_idx 
                    ON sysadmin_timeslot (user_id);
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
    ]

