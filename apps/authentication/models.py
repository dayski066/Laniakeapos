from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class Rol(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='roles_registrados'
    )
    usuario_modificacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='roles_modificados'
    )

    class Meta:
        db_table = 'auth_rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre

class User(AbstractUser):
    foto = models.ImageField(
        upload_to='usuarios/fotos/', 
        null=True, 
        blank=True,
        verbose_name='Foto de perfil'
    )
    rol = models.ForeignKey(
        Rol, 
        on_delete=models.SET_NULL, 
        null=True,
        db_column='rol_id',
        verbose_name='Rol'
    )
    establecimiento = models.ForeignKey(
        'ajustes.Establecimiento',  # Usamos referencia como string porque está en otra app
        on_delete=models.SET_NULL, 
        null=True,
        db_column='establecimiento_id',
        verbose_name='Establecimiento'
    )
    telefono = models.CharField(max_length=15, null=True, blank=True)
    direccion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'