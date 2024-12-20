# apps/ajustes/models.py
from django.db import models
from django.conf import settings

class Establecimiento(models.Model):
    nombre = models.CharField(max_length=200)
    cif = models.CharField(max_length=20, unique=True)
    direccion = models.TextField()
    telefono = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)  # Opcional
    logo = models.ImageField(upload_to='establecimiento/', blank=True, null=True)  # Opcional
    horario = models.TextField(blank=True, null=True)  # Opcional
    terminos_condiciones = models.TextField(blank=True, null=True)  # Opcional
    politica_privacidad = models.TextField(blank=True, null=True)  # Opcional
    redes_sociales = models.TextField(blank=True, null=True)  # Opcional
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='establecimientos_registrados'
    )
    usuario_modificacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='establecimientos_modificados'
    )

    class Meta:
        verbose_name = 'Establecimiento'
        verbose_name_plural = 'Establecimientos'

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    nombre_completo = models.CharField(max_length=200, null=False, blank=False)
    dni = models.CharField(max_length=20, unique=True, null=False, blank=False)
    direccion = models.TextField(null=False, blank=False)
    telefono = models.CharField(max_length=15, null=False, blank=False)
    email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='clientes_registrados'
    )
    usuario_modificacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='clientes_modificados'
    )

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre_completo']

    def __str__(self):
        return f"{self.nombre_completo} - {self.dni}"


class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('success', 'Éxito'),
    ]

    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='info')
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='notificaciones_registradas'
    )
    usuario_modificacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='notificaciones_modificadas'
    )

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.titulo} - {self.usuario_registro}'
