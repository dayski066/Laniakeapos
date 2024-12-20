# apps/sat/models.py
from django.conf import settings
from django.db import models
from decimal import Decimal
from apps.ajustes.models import Cliente
class Reparacion(models.Model):
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="reparaciones"
    )
    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reparaciones_registradas'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    usuario_modificacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reparaciones_modificadas'
    )
    fecha_modificacion = models.DateTimeField(auto_now=True)
    fecha = models.DateTimeField(auto_now_add=True)
    precio = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("en_proceso", "En Proceso"),
        ("finalizado", "Finalizado"),
        ("entregado", "Entregado"),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Reparación'
        verbose_name_plural = 'Reparaciones'

    def __str__(self):
        return f"Reparación {self.id} - {self.cliente.nombre_completo}"

class DetalleReparacion(models.Model):
  reparacion = models.ForeignKey(Reparacion, on_delete=models.CASCADE, related_name='detalles')
  
  TIPO_DISPOSITIVO_CHOICES = [
      ('movil', 'Móvil'),
      ('consola', 'Consola'),
      ('ordenador', 'Ordenador'),
  ]
  
  tipo_dispositivo = models.CharField(max_length=20, choices=TIPO_DISPOSITIVO_CHOICES)
  marca = models.CharField(max_length=100)
  modelo = models.CharField(max_length=100)
  numero_serie = models.CharField(max_length=100)
  averia = models.TextField()
  
  TIPO_BLOQUEO_CHOICES = [
    ('sin_bloqueo', 'Sin Bloqueo'),
    ('patron', 'Patrón'),
    ('pin', 'PIN'),
    ('contraseña', 'Contraseña'),
]
  tipo_bloqueo = models.CharField(max_length=20, choices=TIPO_BLOQUEO_CHOICES, default='sin_bloqueo')  # Nuevo campo
  bloqueo = models.TextField(blank=True, null=True)  # Este campo almacenará el valor del bloqueo (patrón, PIN, etc.)
  precio = models.DecimalField(max_digits=10, decimal_places=2)
  

  def __str__(self):
      return f"{self.get_tipo_dispositivo_display()} - {self.marca} {self.modelo}"
