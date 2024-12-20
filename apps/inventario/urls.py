# urls.py
from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Productos
    path('nuevo/', views.nuevo_producto, name='nuevo_producto'),
    path('almacen/', views.almacen, name='almacen'),
    path('producto/<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('producto/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('producto/<int:pk>/etiqueta/', views.generar_etiqueta, name='generar_etiqueta'),
    
    # Gestión de Categorías y Distribuidores
    path('gestion/', views.gestion, name='gestion'),
    # URLs para categorías
    path('categoria/agregar/', views.agregar_categoria, name='agregar_categoria'),
    path('categoria/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categoria/<int:pk>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
    # URLs para distribuidores
    path('distribuidor/agregar/', views.agregar_distribuidor, name='agregar_distribuidor'),
    path('distribuidor/<int:pk>/editar/', views.editar_distribuidor, name='editar_distribuidor'),
    path('distribuidor/<int:pk>/eliminar/', views.eliminar_distribuidor, name='eliminar_distribuidor'),
]