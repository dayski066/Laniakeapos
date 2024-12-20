from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import User, Rol

@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    print("Signal post_migrate ejecutándose") 
    if kwargs.get('app_config').name == 'apps.authentication':
        print("Dentro de la app authentication") 
        if not User.objects.filter(is_superuser=True).exists():
            try:
                # Crear rol administrador si no existe
                rol_admin, _ = Rol.objects.get_or_create(
                    nombre='Administrador'
                )

                # Crear superusuario
                superuser = User.objects.create_superuser(
                    username="admin",
                    password="admin123",
                    is_active=True,
                    is_staff=True,
                    rol=rol_admin
                )
                print("✅ Superusuario creado exitosamente")
                print("Usuario: admin")
                print("Contraseña: admin123")

            except Exception as e:
                print(f"❌ Error al crear superusuario: {str(e)}")