# apps/compras/forms.py
from django import forms
from .models import Compra

class CompraForm(forms.ModelForm):
    # Campos del cliente
    nombre_completo = forms.CharField(max_length=200)
    dni = forms.CharField(max_length=20)
    direccion = forms.CharField(widget=forms.Textarea)
    telefono = forms.CharField(max_length=15)

    class Meta:
        model = Compra
        fields = ['tipo_dispositivo', 'marca', 'modelo', 'numero_serie',
                 'estado', 'precio', 'nota', 'imagen_dni']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases de Tailwind a todos los campos
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
            'marca': 'Marca del dispositivo',
            'modelo': 'Modelo del dispositivo',
            'numero_serie': 'Número de serie',
            'precio': '0.00',
            'nota': 'Notas adicionales sobre la compra'
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
                'placeholder': 'Notas adicionales sobre la compra'
            })

        # Estilo especial para el campo de imagen
        if 'imagen_dni' in self.fields:
            self.fields['imagen_dni'].widget.attrs.update({
                'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            })