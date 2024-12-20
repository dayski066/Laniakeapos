# forms.py
from django import forms
from .models import Categoria, Distribuidor, Producto

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Nombre de la categoría'
            })
        }

class DistribuidorForm(forms.ModelForm):
    class Meta:
        model = Distribuidor
        fields = ['nombre', 'cif', 'direccion', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Nombre del distribuidor'
            }),
            'cif': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'CIF del distribuidor'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Dirección del distribuidor'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Teléfono del distribuidor'
            })
        }

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['categoria', 'distribuidor', 'nombre', 'cantidad', 'precio_compra', 'precio_venta', 'nota']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases de Tailwind a todos los campos
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            })

        # Añadir placeholders específicos
        field_placeholders = {
            'nombre': 'Nombre del producto',
            'cantidad': '0',
            'precio_compra': '0.00',
            'precio_venta': '0.00',
            'nota': 'Notas adicionales sobre el producto'
        }
        
        for field_name, placeholder in field_placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['placeholder'] = placeholder

        # Configuración específica para campos numéricos
        self.fields['cantidad'].widget.attrs.update({
            'min': '0',
            'type': 'number'
        })
        
        for field in ['precio_compra', 'precio_venta']:
            self.fields[field].widget.attrs.update({
                'min': '0',
                'step': '0.01',
                'type': 'number'
            })

        # Configurar el campo de notas
        self.fields['nota'].widget = forms.Textarea(attrs={
            'rows': '3',
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Notas adicionales sobre el producto'
        })

        # Configuración específica para selects (categoria y distribuidor)
        for field in ['categoria', 'distribuidor']:
            self.fields[field].widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'

    def clean(self):
        cleaned_data = super().clean()
        precio_compra = cleaned_data.get('precio_compra')
        precio_venta = cleaned_data.get('precio_venta')

        if precio_compra and precio_venta:
            if precio_venta < precio_compra:
                raise forms.ValidationError(
                    "El precio de venta no puede ser menor que el precio de compra."
                )

        return cleaned_data