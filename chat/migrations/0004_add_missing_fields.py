import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_auto_20240507_1656'),
        ('profiles', '0003_add_missing_fields'),
    ]

    operations = [
        # ChatRoom: add meeting_id
        migrations.AddField(
            model_name='chatroom',
            name='meeting_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),

        # Membership: add blocked and is_event_admin
        migrations.AddField(
            model_name='membership',
            name='blocked',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='membership',
            name='is_event_admin',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),

        # Message: add content_type and media_url, fix timestamp
        migrations.AddField(
            model_name='message',
            name='content_type',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='media_url',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),

        # CallRoom: add uid, start_time, end_time, duration
        migrations.AddField(
            model_name='callroom',
            name='uid',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='callroom',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='callroom',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='callroom',
            name='duration',
            field=models.IntegerField(default=0),
        ),
        # Remove old timestamp field from CallRoom (replaced by start_time)
        migrations.RemoveField(
            model_name='callroom',
            name='timestamp',
        ),

        # Event: add name, description, room_display_picture; convert event_room to OneToOne
        migrations.AddField(
            model_name='event',
            name='name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='description',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='room_display_picture',
            field=models.ImageField(blank=True, null=True, upload_to='upload/room_picture'),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_room',
            field=models.OneToOneField(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='chat.chatroom',
            ),
        ),

        # MessageAllowance model
        migrations.CreateModel(
            name='MessageAllowance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remaining_messages', models.PositiveIntegerField(default=0)),
                ('last_updated', models.DateTimeField(auto_now=True, blank=True, null=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_allowances', to='profiles.profile')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_allowances', to='profiles.profile')),
            ],
        ),

        # CallDuration model
        migrations.CreateModel(
            name='CallDuration',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('total_minutes', models.IntegerField(default=0)),
                ('profile', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.profile')),
            ],
        ),

        # ReportEvent model
        migrations.CreateModel(
            name='ReportEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('reason', models.CharField(blank=True, max_length=250, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='chat.event')),
                ('reported_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.profile')),
            ],
        ),

        # Remove old AgoraCallToken and AgoraChatToken models (no longer in models.py)
        migrations.DeleteModel(name='AgoraCallToken'),
        migrations.DeleteModel(name='AgoraChatToken'),
    ]
