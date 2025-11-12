# Generated migration to add college field to UserProfile
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0003_add_gender_age'),
    ]

    operations = [
        migrations.RunSQL(
            # Add college column if it doesn't exist
            sql="""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='public_userprofile' AND column_name='college') THEN
                        ALTER TABLE public_userprofile ADD COLUMN college VARCHAR(255) DEFAULT '';
                    END IF;
                END $$;
            """,
            reverse_sql="""
                ALTER TABLE public_userprofile DROP COLUMN IF EXISTS college;
            """
        ),
    ]

