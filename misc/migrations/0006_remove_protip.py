from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('misc', '0005_networkgroup_custom_template'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProTip',
        ),
    ]
