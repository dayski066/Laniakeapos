# apps/ventas/admin.py
from django.contrib import admin
from .models import Venta, DetalleVenta

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    fields = ['tipo_dispositivo', 'marca', 'modelo', 'numero_serie', 'estado', 'precio', 'nota']

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'usuario', 'fecha', 'total')
    list_filter = ('fecha', 'usuario')
    search_fields = ('cliente__nombre_completo', 'cliente__dni', 'detalles__marca', 'detalles__modelo')
    inlines = [DetalleVentaInline]
    readonly_fields = ('fecha',)

    def total(self, obj):
        return f"{obj.total}€"
    total.short_description = 'Total'