# apps/ventas/forms.py
from django import forms
from .models import Venta, DetalleVenta
from apps.ajustes.models import Cliente

class VentaForm(forms.ModelForm):
    # Campos del cliente
    nombre_completo = forms.CharField(max_length=200)
    dni = forms.CharField(max_length=20)
    direccion = forms.CharField(widget=forms.Textarea)
    telefono = forms.CharField(max_length=15)

    class Meta:
        model = Venta
        fields = ['nota']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializar campos del cliente si existe la instancia
        if self.instance and self.instance.pk:
            self.initial['nombre_completo'] = self.instance.cliente.nombre_completo
            self.initial['dni'] = self.instance.cliente.dni
            self.initial['direccion'] = self.instance.cliente.direccion
            self.initial['telefono'] = self.instance.cliente.telefono

        # Aplicar clases de Tailwind a todos los campos - EXACTAMENTE como en CompraForm
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            })

        # Añadir placeholders específicos
        field_placeholders = {
            'nombre_completo': 'Nombre completo del cliente',
            'dni': 'DNI del cliente',
            'direccion': 'Dirección del cliente',
            'telefono': 'Teléfono del cliente',
            'nota': 'Notas adicionales sobre la venta'
        }
        
        for field_name, placeholder in field_placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['placeholder'] = placeholder

        # Configurar campos específicos
        if 'direccion' in self.fields:
            self.fields['direccion'].widget.attrs.update({
                'rows': '3'
            })

        if 'nota' in self.fields:
            self.fields['nota'].widget = forms.Textarea(attrs={
                'rows': '3',
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Notas adicionales sobre la venta'
            })

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['tipo_dispositivo', 'marca', 'modelo', 'numero_serie', 'estado', 'precio', 'nota']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases de Tailwind a todos los campos - EXACTAMENTE como en CompraForm
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            })