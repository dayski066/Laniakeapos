# apps/inventario/admin.py
from django.contrib import admin
from .models import Categoria, Producto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio_venta', 'stock', 'estado')
    list_filter = ('categoria', 'estado')
    search_fields = ('nombre', 'codigo')