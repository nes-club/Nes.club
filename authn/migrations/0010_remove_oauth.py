from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authn', '0009_auto_20230925_1035'),
    ]

    operations = [
        migrations.DeleteModel(name='OAuth2AuthorizationCode'),
        migrations.DeleteModel(name='OAuth2Token'),
        migrations.DeleteModel(name='OAuth2App'),
    ]
