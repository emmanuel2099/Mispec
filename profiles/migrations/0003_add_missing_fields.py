import uuid
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_initial'),
    ]

    operations = [
        # Add missing Profile fields
        migrations.AddField(model_name='profile', name='uid', field=models.IntegerField(blank=True, null=True)),
        migrations.AddField(model_name='profile', name='email', field=models.CharField(blank=True, max_length=200, null=True)),
        migrations.AddField(model_name='profile', name='first_name', field=models.CharField(blank=True, max_length=250, null=True)),
        migrations.AddField(model_name='profile', name='last_name', field=models.CharField(blank=True, max_length=250, null=True)),
        migrations.AddField(model_name='profile', name='profile_picture', field=models.ImageField(blank=True, null=True, upload_to='upload/profile_picture')),
        migrations.AddField(model_name='profile', name='profile_media', field=models.FileField(blank=True, null=True, upload_to='upload/profile_media')),
        migrations.AddField(model_name='profile', name='gender', field=models.CharField(blank=True, choices=[('Male', 'male'), ('Female', 'female')], max_length=100, null=True)),
        migrations.AddField(model_name='profile', name='date_of_birth', field=models.DateField(blank=True, null=True)),
        migrations.AddField(model_name='profile', name='sexual_orientation', field=models.CharField(blank=True, choices=[('Male', 'male'), ('Female', 'female'), ('Both', 'both')], max_length=100, null=True)),
        migrations.AddField(model_name='profile', name='zodiac_sign', field=models.CharField(blank=True, max_length=200, null=True)),
        migrations.AddField(model_name='profile', name='why_are_you_here', field=models.CharField(blank=True, max_length=200, null=True)),
        migrations.AddField(model_name='profile', name='relationship_status', field=models.CharField(blank=True, max_length=200, null=True)),
        migrations.AddField(model_name='profile', name='longitude', field=models.DecimalField(blank=True, decimal_places=6, default=Decimal('0.0'), max_digits=9, null=True)),
        migrations.AddField(model_name='profile', name='latitude', field=models.DecimalField(blank=True, decimal_places=6, default=Decimal('0.0'), max_digits=9, null=True)),
        migrations.AddField(model_name='profile', name='bio', field=models.TextField(blank=True, null=True)),
        migrations.AddField(model_name='profile', name='referral_code', field=models.CharField(blank=True, max_length=100, null=True)),
        migrations.AddField(model_name='profile', name='occupation', field=models.CharField(blank=True, max_length=200, null=True)),
        migrations.AddField(model_name='profile', name='height', field=models.CharField(blank=True, max_digits=200, null=True) if False else models.CharField(blank=True, max_length=200, null=True)),
        migrations.AddField(model_name='profile', name='fcm_token', field=models.CharField(blank=True, max_length=250, null=True)),
        migrations.AddField(model_name='profile', name='is_location', field=models.BooleanField(blank=True, default=False, null=True)),
        migrations.AddField(model_name='profile', name='is_incognito', field=models.BooleanField(blank=True, default=False, null=True)),
        migrations.AddField(model_name='profile', name='is_like_notification', field=models.BooleanField(blank=True, default=True, null=True)),
        migrations.AddField(model_name='profile', name='is_match_notification', field=models.BooleanField(blank=True, default=True, null=True)),
        migrations.AddField(model_name='profile', name='is_gift_notification', field=models.BooleanField(blank=True, default=True, null=True)),
        migrations.AddField(model_name='profile', name='is_chat_notification', field=models.BooleanField(blank=True, default=True, null=True)),
        migrations.AddField(model_name='profile', name='is_event_notification', field=models.BooleanField(blank=True, default=True, null=True)),
        migrations.AddField(model_name='profile', name='is_verified', field=models.BooleanField(blank=True, default=False, null=True)),
        migrations.AddField(model_name='profile', name='location_name', field=models.CharField(blank=True, max_length=250, null=True)),
        migrations.AddField(model_name='profile', name='distance', field=models.CharField(blank=True, max_length=250, null=True)),

        # Add entertainment M2M
        migrations.AddField(model_name='profile', name='entertainment', field=models.ManyToManyField(blank=True, to='profiles.entertainment')),

        # Fix Like model - rename reciever to receiver
        migrations.RenameField(model_name='like', old_name='reciever', new_name='receiver'),

        # Add Plan FK to profile
        migrations.AddField(
            model_name='profile',
            name='plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.plan'),
        ),

        # Create ProfileGift model
        migrations.CreateModel(
            name='ProfileGift',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('gift_type', models.CharField(blank=True, choices=[('bought', 'Bought'), ('received', 'Received')], max_length=100, null=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('is_reedemed', models.BooleanField(blank=True, default=False, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('gift', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.gift')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_gifts', to='profiles.profile')),
            ],
        ),

        # Create Match model
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('profile_a', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile_a', to='profiles.profile')),
                ('profile_b', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile_b', to='profiles.profile')),
            ],
            options={'verbose_name_plural': 'Matches'},
        ),

        # Create Notification model
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(blank=True, max_length=255, null=True)),
                ('notification_type', models.CharField(blank=True, choices=[('chat', 'Chat Notification'), ('like', 'Like Notification'), ('match', 'Match Notification'), ('gift', 'Gift Notification'), ('event', 'Event Notification')], max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('is_read', models.BooleanField(blank=True, default=False, null=True)),
                ('recipient', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.profile')),
            ],
        ),

        # Create UserPlan model
        migrations.CreateModel(
            name='UserPlan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('expiry_date', models.DateTimeField(db_index=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('plan', models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.plan')),
                ('profile', models.OneToOneField(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.profile')),
            ],
        ),

        # Create Support model
        migrations.CreateModel(
            name='Support',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.profile')),
            ],
        ),

        # Remove old reports M2M and gifting model refs that no longer exist
        migrations.RemoveField(model_name='profile', name='reports'),
    ]
