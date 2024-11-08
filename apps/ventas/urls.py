# apps/ventas/urls.py
from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('nueva/', views.nueva_venta, name='nueva_venta'),
    path('verificar-dni/', views.verificar_dni, name='verificar_dni'),
    path('historial/', views.historial_ventas, name='historial_ventas'),
    path('factura-pdf/<int:venta_id>/', views.generar_factura_pdf, name='generar_factura_pdf'),
    path('editar/<int:venta_id>/', views.editar_venta, name='editar_venta'),
    path('eliminar/<int:venta_id>/', views.eliminar_venta, name='eliminar_venta'),
    path('obtener-venta/<int:venta_id>/', views.obtener_venta, name='obtener_venta'),
    # URLs para manejar detalles de venta
    path('editar-detalle/<int:detalle_id>/', views.editar_detalle_venta, name='editar_detalle_venta'),
    path('agregar-detalle/', views.agregar_detalle_venta, name='agregar_detalle_venta'),
    path('eliminar-detalle/<int:detalle_id>/', views.eliminar_detalle_venta, name='eliminar_detalle_venta'),
]