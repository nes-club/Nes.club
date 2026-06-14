from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0037_alter_user_membership_platform_type"),
    ]
    operations = [
        migrations.RemoveField(
            model_name="user",
            name="stripe_id",
        ),
    ]
