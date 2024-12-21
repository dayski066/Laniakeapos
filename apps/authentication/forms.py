from django import forms
from django.contrib.auth import get_user_model
from .models import Rol

User = get_user_model()

class UserForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'username', 
            'first_name', 
            'last_name', 
            'email', 
            'telefono', 
            'direccion', 
            'foto', 
            'rol', 
            'establecimiento',  # Añadimos este campo
            'is_active'
        ]
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono', 
                 'direccion', 'foto', 'rol', 'is_active']
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }

class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = ['nombre']