# apps/compras/admin.py
from django.contrib import admin
from .models import Cliente, Compra



@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo_dispositivo', 'marca', 'precio', 'fecha')
    list_filter = ('tipo_dispositivo', 'estado')
    search_fields = ('cliente__nombre_completo', 'modelo', 'numero_serie')