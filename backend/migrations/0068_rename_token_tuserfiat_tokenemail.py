# Generated by Django 4.0.4 on 2023-02-16 17:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0067_rename_codigo_tuserfiat_token_tuserfiat_creacion_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tuserfiat',
            old_name='token',
            new_name='tokenemail',
        ),
    ]
