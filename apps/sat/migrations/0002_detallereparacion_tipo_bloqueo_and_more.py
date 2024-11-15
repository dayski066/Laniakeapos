# Generated by Django 5.1.2 on 2024-11-05 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='detallereparacion',
            name='tipo_bloqueo',
            field=models.CharField(choices=[('sin_bloqueo', 'Sin Bloqueo'), ('patron', 'Patrón'), ('pin', 'PIN'), ('huella', 'Huella'), ('facial', 'Facial')], default='sin_bloqueo', max_length=20),
        ),
        migrations.AlterField(
            model_name='detallereparacion',
            name='bloqueo',
            field=models.TextField(blank=True, null=True),
        ),
    ]
