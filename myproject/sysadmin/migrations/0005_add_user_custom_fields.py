# Generated migration to add custom fields to auth_user table
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sysadmin', '0004_delete_counselor'),
    ]

    operations = [
        migrations.RunSQL(
            # Add custom fields to auth_user table if they don't exist
            sql="""
                DO $$ 
                BEGIN
                    -- Add middle_initial column if it doesn't exist
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='auth_user' AND column_name='middle_initial') THEN
                        ALTER TABLE auth_user ADD COLUMN middle_initial VARCHAR(10);
                    END IF;
                    
                    -- Add assigned_college column if it doesn't exist
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='auth_user' AND column_name='assigned_college') THEN
                        ALTER TABLE auth_user ADD COLUMN assigned_college VARCHAR(255);
                    END IF;
                    
                    -- Add title column if it doesn't exist
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='auth_user' AND column_name='title') THEN
                        ALTER TABLE auth_user ADD COLUMN title VARCHAR(255);
                    END IF;
                    
                    -- Add bio column if it doesn't exist
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='auth_user' AND column_name='bio') THEN
                        ALTER TABLE auth_user ADD COLUMN bio TEXT;
                    END IF;
                    
                    -- Add image_data column if it doesn't exist
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='auth_user' AND column_name='image_data') THEN
                        ALTER TABLE auth_user ADD COLUMN image_data BYTEA;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                -- Remove columns if rolling back (optional)
                ALTER TABLE auth_user DROP COLUMN IF EXISTS middle_initial;
                ALTER TABLE auth_user DROP COLUMN IF EXISTS assigned_college;
                ALTER TABLE auth_user DROP COLUMN IF EXISTS title;
                ALTER TABLE auth_user DROP COLUMN IF EXISTS bio;
                ALTER TABLE auth_user DROP COLUMN IF EXISTS image_data;
            """
        ),
    ]

