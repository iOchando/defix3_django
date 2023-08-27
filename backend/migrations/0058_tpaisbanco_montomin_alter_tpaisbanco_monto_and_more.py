# Generated by Django 4.0.4 on 2022-12-19 17:27

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0057_alter_fiattransaccion_adjuntofiat_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tpaisbanco',
            name='montomin',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), help_text='Monto minimo validar para venta', max_digits=14),
        ),
        migrations.AlterField(
            model_name='tpaisbanco',
            name='monto',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), help_text='Monto limite para validar para venta', max_digits=14),
        ),
        migrations.AlterField(
            model_name='tpaisbanco',
            name='tasa',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), help_text='tasa venta', max_digits=14),
        ),
        migrations.AlterField(
            model_name='tpaisbanco',
            name='tasaaltomonto',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), help_text='tasa a aplicar con altos montos de venta', max_digits=14),
        ),
    ]