# apps/authentication/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import UserForm, UserEditForm, RolForm
from .models import Rol
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.urls import reverse

User = get_user_model()

@login_required
def listar_usuarios(request):
    usuarios = User.objects.select_related('rol').all()
    return render(request, 'ajustes/listar_usuarios.html', {
        'usuarios': usuarios
    })

@login_required
def crear_usuario(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.usuario_registro = request.user
            usuario.save()
            # Usamos messages y redirect que sabemos que funciona
            messages.success(request, 'Usuario creado correctamente')
            return redirect('auth:listar_usuarios')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = UserForm()

    roles = Rol.objects.all()
    return render(request, 'ajustes/crear_usuario.html', {
        'form': form,
        'roles': roles
    })

@login_required
def editar_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    roles = Rol.objects.all()  # Obtenemos todos los roles

    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.usuario_modificacion = request.user

            # Manejamos el rol
            nuevo_rol_id = request.POST.get('rol')
            if nuevo_rol_id:
                usuario.rol_id = nuevo_rol_id

            # Manejo de la contraseña
            nueva_password = request.POST.get('new_password')
            confirmar_password = request.POST.get('confirm_password')
            if nueva_password and confirmar_password and nueva_password == confirmar_password:
                usuario.set_password(nueva_password)

            usuario.save()
            messages.success(request, 'Usuario actualizado correctamente')
            return redirect('auth:listar_usuarios')
    else:
        form = UserEditForm(instance=usuario)

    return render(request, 'ajustes/editar_usuario.html', {
        'form': form,
        'usuario': usuario,
        'roles': roles  # Pasamos los roles a la plantilla
    })

@login_required
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    try:
        if request.method == 'POST':
            usuario.delete()
            return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False})
    
class CustomLoginView(LoginView):
   template_name = 'authentication/login.html'
   redirect_authenticated_user = True
   success_url = reverse_lazy('auth:home')

   def get_success_url(self):
       return self.success_url

   def form_invalid(self, form):
       messages.error(self.request, 'Usuario o contraseña incorrectos')
       return super().form_invalid(form)

@login_required 
def home(request):
   return render(request, 'home.html', {
       'title': 'Dashboard'
   })


@login_required
def listar_roles(request):
    roles = Rol.objects.all()
    return render(request, 'ajustes/listar_roles.html', {
        'roles': roles
    })

@login_required
def crear_rol(request):
    if request.method == 'POST':
        form = RolForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rol creado correctamente')
            return redirect('auth:listar_roles')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = RolForm()

    return render(request, 'ajustes/crear_rol.html', {
        'form': form
    })

@login_required
def editar_rol(request, pk):
    rol = get_object_or_404(Rol, pk=pk)
    if request.method == 'POST':
        form = RolForm(request.POST, instance=rol)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rol actualizado correctamente')
            return redirect('auth:listar_roles')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = RolForm(instance=rol)

    return render(request, 'ajustes/editar_rol.html', {
        'form': form,
        'rol': rol
    })

@login_required
def eliminar_rol(request, pk):
    rol = get_object_or_404(Rol, pk=pk)
    try:
        if request.method == 'POST':
            rol.delete()
            return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False})