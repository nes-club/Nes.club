# Generated by Django 3.2.13 on 2024-02-18 18:10

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0027_auto_20230808_1201'),
        ('rooms', '0003_auto_20230925_1239'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('json_text', models.JSONField()),
                ('channel_msg_id', models.CharField(blank=True, max_length=32, null=True, unique=True)),
                ('discussion_msg_id', models.CharField(blank=True, max_length=32, null=True)),
                ('room_chat_msg_id', models.CharField(blank=True, max_length=32, null=True)),
                ('room', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='rooms.room')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.user')),
            ],
            options={
                'db_table': 'questions',
            },
        ),
        migrations.CreateModel(
            name='HelpDeskUser',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('banned_until', models.DateTimeField(null=True)),
                ('ban_reason', models.CharField(max_length=512, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user')),
            ],
            options={
                'db_table': 'help_desk_users',
            },
        ),
    ]