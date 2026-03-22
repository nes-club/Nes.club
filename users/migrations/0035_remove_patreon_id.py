from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_alter_friend_options_alter_user_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='patreon_id',
        ),
    ]
