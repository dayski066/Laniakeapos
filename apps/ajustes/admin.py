# apps/ajustes/admin.py
from django.contrib import admin
from .models import Establecimiento, Cliente, Notificacion

@admin.register(Establecimiento)
class EstablecimientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cif', 'telefono', 'email')
    search_fields = ('nombre', 'cif')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'dni', 'telefono', 'email')
    search_fields = ('nombre_completo', 'dni', 'telefono')
    list_filter = ('created_at',)

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'fecha', 'usuario_registro', 'tipo', 'leida']  # Cambiado 'usuario' por 'usuario_registro'
    list_filter = ['tipo', 'leida']
    search_fields = ['titulo', 'mensaje']

