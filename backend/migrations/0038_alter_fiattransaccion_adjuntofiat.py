# Generated by Django 4.0.4 on 2022-11-10 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0037_fiattransaccion_adjuntofiat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fiattransaccion',
            name='adjuntofiat',
            field=models.ImageField(blank=True, default='default.jpg', help_text='adjunto soporte de la venta o compra', null=True, upload_to='fiat'),
        ),
    ]