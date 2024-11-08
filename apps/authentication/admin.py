# apps/authentication/admin.py
from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefono', 'created_at')
    search_fields = ('user__username', 'telefono')