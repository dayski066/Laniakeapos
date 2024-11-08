# apps/ventas/models.py
from django.db import models
from django.contrib.auth.models import User
from apps.ajustes.models import Cliente

class Venta(models.Model):
    TIPO_CHOICES = [
        ('movil', 'Móvil'),
        ('consola', 'Consola'),
        ('ordenador', 'Ordenador'),
    ]
    
    ESTADO_CHOICES = [
        ('nuevo', 'Nuevo'),
        ('usado', 'Usado'),
        ('km0', 'KM0'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    nota = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Venta {self.id} - {self.cliente.nombre_completo}"

    @property
    def total(self):
        return sum(detalle.precio for detalle in self.detalles.all())
    
    @property
    def base_imponible(self):
        return round(float(self.total) / 1.21, 2)
    
    @property
    def iva(self):
        return round(self.total - self.base_imponible, 2)

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    tipo_dispositivo = models.CharField(max_length=20, choices=Venta.TIPO_CHOICES)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    numero_serie = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=Venta.ESTADO_CHOICES)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    nota = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.numero_serie}"