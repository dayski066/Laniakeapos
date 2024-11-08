# apps/sat/forms.py
from django import forms
from .models import Reparacion, DetalleReparacion
from apps.ajustes.models import Cliente

class ReparacionForm(forms.ModelForm):
    # Campos del cliente que no están en el modelo Reparacion
    nombre_completo = forms.CharField(max_length=200)
    dni = forms.CharField(max_length=20)
    direccion = forms.CharField(max_length=200)
    telefono = forms.CharField(max_length=20)
    
    class Meta:
        model = Reparacion
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['nombre_completo'] = self.instance.cliente.nombre_completo
            self.initial['dni'] = self.instance.cliente.dni
            self.initial['direccion'] = self.instance.cliente.direccion
            self.initial['telefono'] = self.instance.cliente.telefono

        # Aplicar clases de Tailwind a todos los campos
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            })

class DetalleReparacionForm(forms.ModelForm):
    class Meta:
        model = DetalleReparacion
        fields = ['tipo_dispositivo', 'marca', 'modelo', 'numero_serie', 
                 'tipo_bloqueo', 'bloqueo', 'precio', 'averia']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar el campo tipo_bloqueo
        self.fields['tipo_bloqueo'] = forms.ChoiceField(
            choices=[
                ('sin_bloqueo', 'Sin Bloqueo'),
                ('patron', 'Patrón'),
                ('pin', 'PIN'),
                ('contraseña', 'Contraseña')
            ],
            widget=forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            })
        )

        # Configurar el campo bloqueo
        self.fields['bloqueo'].widget = forms.TextInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
        })

        # Aplicar clases de Tailwind a todos los demás campos
        for field_name, field in self.fields.items():
            if field_name not in ['tipo_bloqueo', 'bloqueo']:
                field.widget.attrs.update({
                    'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
                })