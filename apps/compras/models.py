# apps/compras/models.py
from django.db import models
from django.contrib.auth.models import User
from apps.ajustes.models import Cliente  # Importamos Cliente desde ajustes

class Compra(models.Model):
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

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)  # Referencia al Cliente de ajustes
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_dispositivo = models.CharField(max_length=20, choices=TIPO_CHOICES, null=False, blank=False)
    marca = models.CharField(max_length=100, null=False, blank=False)
    modelo = models.CharField(max_length=100, null=False, blank=False)
    numero_serie = models.CharField(max_length=100, null=False, blank=False)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, null=False, blank=False)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    nota = models.TextField(null=False, blank=False)
    imagen_dni = models.ImageField(upload_to='dnis/', null=False, blank=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Compra {self.id} - {self.cliente.nombre_completo}"