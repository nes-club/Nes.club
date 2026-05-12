from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("badges", "0005_alter_userbadge_options"),
    ]
    operations = [
        migrations.AlterModelOptions(
            name="badge",
            options={"ordering": ["code"]},
        ),
        migrations.RemoveField(
            model_name="badge",
            name="price_days",
        ),
    ]
