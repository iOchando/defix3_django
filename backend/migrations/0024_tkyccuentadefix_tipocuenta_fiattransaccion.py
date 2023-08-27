# Generated by Django 4.0.4 on 2022-11-07 15:52

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('backend', '0023_alter_tpais_tasa'),
    ]

    operations = [
        migrations.AddField(
            model_name='tkyccuentadefix',
            name='tipocuenta',
            field=models.TextField(blank=True, help_text='tipo  de cuenta del titular', max_length=20, null=True),
        ),
        migrations.CreateModel(
            name='FiatTransaccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estatus', models.CharField(choices=[('C', 'Creado'), ('A', 'Asignado'), ('P', 'Procesado'), ('C', 'Completado'), ('X', 'Anulado')], default='R', max_length=1)),
                ('accion', models.CharField(choices=[('C', 'Creado'), ('A', 'Asignado'), ('P', 'Procesado'), ('C', 'Completado'), ('X', 'Anulado')], default='C', max_length=1)),
                ('referencia', models.TextField(blank=True, help_text='numero de referencia', max_length=20, null=True)),
                ('cripto', models.TextField(blank=True, help_text='nombre de la criptomoneda', max_length=20, null=True)),
                ('tasa', models.TextField(blank=True, help_text='tasa', max_length=20, null=True)),
                ('comision', models.TextField(blank=True, help_text='comision', max_length=20, null=True)),
                ('monto', models.TextField(blank=True, help_text='monto', max_length=20, null=True)),
                ('banco_nombre', models.TextField(blank=True, help_text='Nombre del Titular', max_length=150, null=True)),
                ('tipopago_nombre', models.TextField(blank=True, help_text='Nombre del Titular', max_length=150, null=True)),
                ('titular', models.TextField(blank=True, help_text='Nombre del Titular', max_length=150, null=True)),
                ('cedula', models.TextField(blank=True, help_text='Numero de Identificacion', max_length=20, null=True)),
                ('telefono', models.TextField(blank=True, help_text='Numero de telefono del titular', max_length=50, null=True)),
                ('numerocuenta', models.TextField(blank=True, help_text='numero de cuenta del titular', max_length=20, null=True)),
                ('tipocuenta', models.TextField(blank=True, help_text='tipo  de cuenta del titular', max_length=20, null=True)),
                ('fecha_creado', models.DateTimeField(blank=True, default=datetime.datetime.now, help_text='fecha de registro')),
                ('fecha_asignado', models.DateTimeField(blank=True, default=datetime.datetime.now, help_text='fecha de registro')),
                ('usuario_asignado', models.TextField(blank=True, help_text='usuario asignador', max_length=240, null=True)),
                ('fecha_procesado', models.DateTimeField(blank=True, default=datetime.datetime.now, help_text='fecha de registro procesado')),
                ('fecha_completado', models.DateTimeField(blank=True, default=datetime.datetime.now, help_text='fecha de registro completado')),
                ('fecha_anulado', models.DateTimeField(blank=True, default=datetime.datetime.now, help_text='fecha de registro aunulado')),
                ('observacion', models.TextField(blank=True, help_text='usuario', max_length=240, null=True)),
                ('banco', models.ForeignKey(blank=True, help_text='Id de Banco Pais', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='backend.tpaisbanco')),
                ('pais', models.ForeignKey(blank=True, help_text='Pais asociado', null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.tpais')),
                ('tipopago', models.ForeignKey(blank=True, help_text='Id de tipo de pago', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='backend.ttipopago')),
                ('usuario', models.ForeignKey(help_text='usuario asociado', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]