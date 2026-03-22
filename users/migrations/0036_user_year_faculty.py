from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0035_remove_patreon_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='year_of_graduation',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='faculty',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
