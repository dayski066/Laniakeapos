# apps/sat/urls.py
from django.urls import path
from . import views

app_name = 'sat'

urlpatterns = [
    path('nueva/', views.nueva_reparacion, name='nueva_reparacion'),
    path('verificar-dni/', views.verificar_dni, name='verificar_dni'),
    path('historial/', views.historial_reparaciones, name='historial_reparaciones'),
    path('orden-pdf/<int:reparacion_id>/', views.generar_orden_pdf, name='generar_orden_pdf'),
    path('editar/<int:reparacion_id>/', views.editar_reparacion, name='editar_reparacion'),
    path('eliminar/<int:reparacion_id>/', views.eliminar_reparacion, name='eliminar_reparacion'),
    path('eliminar-detalle/<int:detalle_id>/', views.eliminar_detalle_reparacion, name='eliminar_detalle'),  # Añadida esta línea
]