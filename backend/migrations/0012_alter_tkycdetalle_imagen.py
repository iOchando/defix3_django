# Generated by Django 4.0.4 on 2022-10-24 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0011_alter_tkyccabecera_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tkycdetalle',
            name='imagen',
            field=models.ImageField(default='archivoskyc/default.jpg', help_text='Imagen KYC', null=True, upload_to='archivoskyc'),
        ),
    ]