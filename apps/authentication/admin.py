# apps/authentication/admin.py
from django.contrib import admin
from .models import User, Rol  # Cambiar Profile por los modelos que realmente tenemos

# Registrar los modelos
admin.site.register(User)
admin.site.register(Rol)