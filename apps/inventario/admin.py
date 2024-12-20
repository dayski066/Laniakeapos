# apps/inventario/admin.py
from django.contrib import admin
from .models import Categoria, Distribuidor, Producto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    ordering = ('nombre',)

@admin.register(Distribuidor)
class DistribuidorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cif', 'telefono')
    search_fields = ('nombre', 'cif', 'telefono')
    ordering = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'distribuidor', 'codigo_ean', 'cantidad', 'precio_compra', 'precio_venta', 'fecha_registro')
    list_filter = ('categoria', 'distribuidor')
    search_fields = ('nombre', 'codigo_ean')
    ordering = ('-fecha_registro',)
    readonly_fields = ('codigo_ean', 'fecha_registro')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'categoria', 'distribuidor')
        }),
        ('Detalles', {
            'fields': ('cantidad', 'precio_compra', 'precio_venta', 'codigo_ean')
        }),
        ('Información Adicional', {
            'fields': ('nota', 'fecha_registro'),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj: # Si es una edición
            return self.readonly_fields
        return ('fecha_registro',) # Si es nuevo, solo fecha_registro es readonly