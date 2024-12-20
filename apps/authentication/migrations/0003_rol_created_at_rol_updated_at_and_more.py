# Generated by Django 5.1.2 on 2024-12-21 10:06

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajustes', '0004_remove_cliente_fecha_modificacion_and_more'),
        ('authentication', '0002_user_direccion_user_telefono'),
    ]

    operations = [
        migrations.AddField(
            model_name='rol',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rol',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='rol',
            name='usuario_modificacion',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='roles_modificados', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='rol',
            name='usuario_registro',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='roles_registrados', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='establecimiento',
            field=models.ForeignKey(db_column='establecimiento_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='ajustes.establecimiento', verbose_name='Establecimiento'),
        ),
    ]
