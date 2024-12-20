# models.py
from django.db import models
from django.core.validators import MinValueValidator
import random
from django.conf import settings

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre

class Distribuidor(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    cif = models.CharField(max_length=20, unique=True)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Distribuidor'
        verbose_name_plural = 'Distribuidores'

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    distribuidor = models.ForeignKey(
        Distribuidor, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos'
    )
    nombre = models.CharField(max_length=200)
    cantidad = models.IntegerField(validators=[MinValueValidator(0)])
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_ean = models.CharField(max_length=13, unique=True)
    nota = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='productos_registrados'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    usuario_modificacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='productos_modificados'
    )
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.codigo_ean:
            self.codigo_ean = self.generar_ean13()
        super().save(*args, **kwargs)

    def generar_ean13(self):
     while True:
        # Prefijo para España (84)
        prefix = "84"
        # Generamos 10 dígitos aleatorios (en lugar de 9)
        body = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        # Concatenamos prefix y body para tener 12 dígitos
        number = prefix + body
        
        # Verificamos que tengamos exactamente 12 dígitos antes de calcular el dígito de control
        if len(number) != 12:
            continue
            
        # Cálculo del dígito de control
        sum_odd = sum(int(number[i]) for i in range(0, 12, 2))
        sum_even = sum(int(number[i]) * 3 for i in range(1, 12, 2))
        total_sum = sum_odd + sum_even
        check_digit = (10 - (total_sum % 10)) % 10
        
        # Creamos el código EAN13 completo
        ean = number + str(check_digit)
        
        # Verificamos que no exista ya en la base de datos
        if not type(self).objects.filter(codigo_ean=ean).exists():
            return ean