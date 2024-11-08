# apps/sat/apps.py
from django.apps import AppConfig

class SatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sat'
    verbose_name = 'Servicio Técnico'