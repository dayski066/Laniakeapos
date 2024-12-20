from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Establecimiento
from .forms import EstablecimientoForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Vista para listar establecimientos
@login_required
def listar_establecimientos(request):
    # Obtener todos los establecimientos de la base de datos
    establecimientos = Establecimiento.objects.all()
    
    # Renderizar la página con la lista de establecimientos
    return render(request, 'ajustes/listar_establecimientos.html', {'establecimientos': establecimientos})

# Vista para crear un nuevo establecimiento
@login_required
def crear_establecimiento(request):
    if request.method == 'POST':
        form = EstablecimientoForm(request.POST, request.FILES)
        if form.is_valid():
            establecimiento = form.save(commit=False)
            # Campos que se auto-generan
            establecimiento.usuario_registro = request.user
            # No asignamos usuario_modificacion ni updated_at durante la creación
            establecimiento.save()
            messages.success(request, 'Establecimiento creado correctamente')
            return redirect('ajustes:listar_establecimientos')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = EstablecimientoForm()

    return render(request, 'ajustes/crear_establecimiento.html', {
        'form': form
    })

# Vista para editar un establecimiento existente
@login_required
def editar_establecimiento(request, pk):
    # Obtener el establecimiento a editar
    establecimiento = get_object_or_404(Establecimiento, pk=pk)

    if request.method == 'POST':
        form = EstablecimientoForm(request.POST, request.FILES, instance=establecimiento)
        if form.is_valid():
            establecimiento = form.save(commit=False)
            establecimiento.usuario_modificacion = request.user
            establecimiento.save()
            messages.success(request, 'Establecimiento actualizado correctamente')
            return redirect('ajustes:listar_establecimientos')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = EstablecimientoForm(instance=establecimiento)

    return render(request, 'ajustes/editar_establecimiento.html', {
        'form': form,
        'establecimiento': establecimiento
    })

# Vista para eliminar un establecimiento

@login_required
def eliminar_establecimiento(request, pk):
    # Obtener el establecimiento que se quiere eliminar
    establecimiento = get_object_or_404(Establecimiento, pk=pk)

    # Si el método de la solicitud es POST, significa que el usuario ha confirmado la eliminación
    if request.method == 'POST':
        establecimiento.delete()  # Eliminar el establecimiento de la base de datos
        messages.success(request, 'Establecimiento eliminado correctamente')  # Mensaje de éxito
        return JsonResponse({'success': True, 'message': 'Establecimiento eliminado correctamente'})

    # Si no es una solicitud POST, no hacer nada
    return JsonResponse({'success': False, 'message': 'Error al intentar eliminar el establecimiento'})

