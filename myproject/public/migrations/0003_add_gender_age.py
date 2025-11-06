from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0002_studentid_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(max_length=32, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='age',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
    ]


