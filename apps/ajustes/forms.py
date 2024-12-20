from django import forms
from .models import Establecimiento

class EstablecimientoForm(forms.ModelForm):
    class Meta:
        model = Establecimiento
        fields = [
            'nombre',
            'cif',
            'direccion',
            'telefono',
            'email',
            'logo',
            'horario',
            'terminos_condiciones',
            'politica_privacidad',
            'redes_sociales',
        ]
        widgets = {
            'terminos_condiciones': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'politica_privacidad': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'horario': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'direccion': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and '@' not in email:  # Verifica solo si el email no está vacío
            raise forms.ValidationError("El correo electrónico no es válido.")
        return email

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono:
            raise forms.ValidationError("El número de teléfono es obligatorio.")
        if len(telefono) != 9 or not telefono.isdigit():  # Valida que tenga exactamente 9 dígitos numéricos
            raise forms.ValidationError("El número de teléfono debe tener exactamente 9 dígitos numéricos.")
        return telefono
