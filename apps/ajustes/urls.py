# apps/ajustes/urls.py
from django.urls import path
from . import views

app_name = 'ajustes'

urlpatterns = [
    path(
        "establecimientos/",
        views.listar_establecimientos,
        name="listar_establecimientos",
    ),
    path(
        "establecimientos/crear/",
        views.crear_establecimiento,
        name="crear_establecimiento",
    ),
    path(
        "establecimientos/<int:pk>/editar/",
        views.editar_establecimiento,
        name="editar_establecimiento",
    ),
    path(
        "establecimientos/eliminar/<int:pk>/",
        views.eliminar_establecimiento,
        name="eliminar_establecimiento",
    ),
]