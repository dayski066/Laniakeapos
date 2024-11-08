# apps/compras/urls.py
from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    path('nueva/', views.nueva_compra, name='nueva_compra'),
    path('verificar-dni/', views.verificar_dni, name='verificar_dni'),
    path('historial/', views.historial_compras, name='historial_compras'),
    path('contrato-pdf/<int:compra_id>/', views.generar_contrato_pdf, name='generar_contrato_pdf'),
    path('editar/<int:compra_id>/', views.editar_compra, name='editar_compra'),
    path('eliminar/<int:compra_id>/', views.eliminar_compra, name='eliminar_compra'),
    path('obtener-compra/<int:compra_id>/', views.obtener_compra, name='obtener_compra'),
]