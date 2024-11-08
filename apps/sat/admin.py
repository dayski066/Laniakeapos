# apps/sat/admin.py
from django.contrib import admin
from .models import Reparacion, DetalleReparacion

class DetalleReparacionInline(admin.TabularInline):
  model = DetalleReparacion
  extra = 1

@admin.register(Reparacion)
class ReparacionAdmin(admin.ModelAdmin):
  list_display = ('id', 'cliente', 'fecha', 'estado', 'get_total')
  list_filter = ('fecha',)  # Solo filtrar por fecha, sin estado
  search_fields = ('cliente__nombre_completo', 'cliente__dni')
  inlines = [DetalleReparacionInline]

  def get_total(self, obj):
      return sum(detalle.precio for detalle in obj.detalles.all())
  get_total.short_description = 'Total'

@admin.register(DetalleReparacion)
class DetalleReparacionAdmin(admin.ModelAdmin):
  list_display = ('id', 'reparacion', 'tipo_dispositivo', 'marca', 'modelo', 'precio')
  list_filter = ('tipo_dispositivo',)  # Filtrar solo por tipo de dispositivo
  search_fields = ('marca', 'modelo', 'numero_serie')