from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'auth'

urlpatterns = [
    # Rutas existentes de autenticación
    path('', views.home, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='auth:login'), name='logout'),
    
    # Rutas de gestión de usuarios
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:pk>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:pk>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    path('roles/', views.listar_roles, name='listar_roles'),
    path('roles/crear/', views.crear_rol, name='crear_rol'),
    path('roles/<int:pk>/editar/', views.editar_rol, name='editar_rol'),
    path('roles/<int:pk>/eliminar/', views.eliminar_rol, name='eliminar_rol'),
]