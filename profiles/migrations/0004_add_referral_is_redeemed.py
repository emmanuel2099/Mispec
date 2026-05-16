from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_add_missing_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='referral',
            name='is_redeemed',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
