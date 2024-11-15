# Generated by Django 5.1.2 on 2024-11-07 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sat', '0002_detallereparacion_tipo_bloqueo_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detallereparacion',
            name='nota',
        ),
        migrations.RemoveField(
            model_name='reparacion',
            name='averia',
        ),
        migrations.RemoveField(
            model_name='reparacion',
            name='nota',
        ),
        migrations.AddField(
            model_name='detallereparacion',
            name='averia',
            field=models.TextField(default='Sin especificar'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='detallereparacion',
            name='tipo_bloqueo',
            field=models.CharField(choices=[('sin_bloqueo', 'Sin Bloqueo'), ('patron', 'Patrón'), ('pin', 'PIN'), ('contraseña', 'Contraseña')], default='sin_bloqueo', max_length=20),
        ),
    ]
