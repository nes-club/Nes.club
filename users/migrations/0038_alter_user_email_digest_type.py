# Generated manually — remove the legacy "daily" digest choice

from django.db import migrations, models


def daily_to_weekly(apps, schema_editor):
    User = apps.get_model("users", "User")
    User.objects.filter(email_digest_type="daily").update(email_digest_type="weekly")


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0037_alter_user_membership_platform_type'),
    ]

    operations = [
        migrations.RunPython(daily_to_weekly, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='user',
            name='email_digest_type',
            field=models.CharField(
                choices=[('nope', 'Nothing'), ('weekly', 'Weekly')],
                default='weekly', max_length=16,
            ),
        ),
    ]
