# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from .models import Categoria, Distribuidor, Producto
from .forms import CategoriaForm, DistribuidorForm, ProductoForm
from barcode import EAN13
from barcode.writer import ImageWriter
import io
import base64
from django.db.models import Q

@login_required
def gestion(request):
    # Obtener categorías y distribuidores con paginación
    categorias = Categoria.objects.all()
    distribuidores = Distribuidor.objects.all()
    
    # Búsqueda
    query = request.GET.get('q', '')
    if query:
        categorias = categorias.filter(nombre__icontains=query)
        distribuidores = distribuidores.filter(
            nombre__icontains=query) | distribuidores.filter(
            cif__icontains=query) | distribuidores.filter(
            telefono__icontains=query)

    # Paginación
    paginator_cat = Paginator(categorias, 10)
    paginator_dist = Paginator(distribuidores, 10)
    
    page_cat = request.GET.get('page_cat')
    page_dist = request.GET.get('page_dist')
    
    categorias = paginator_cat.get_page(page_cat)
    distribuidores = paginator_dist.get_page(page_dist)

    context = {
        'categorias': categorias,
        'distribuidores': distribuidores,
        'categoria_form': CategoriaForm(),
        'distribuidor_form': DistribuidorForm(),
    }
    
    return render(request, 'inventario/gestion.html', context)

@login_required
def agregar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Categoría agregada correctamente',
                'categoria': {
                    'id': categoria.id,
                    'nombre': categoria.nombre
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

@login_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Categoría actualizada correctamente',
                'categoria': {
                    'id': categoria.id,
                    'nombre': categoria.nombre
                }
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

@login_required
def eliminar_categoria(request, pk):
    if request.method == 'POST':
        categoria = get_object_or_404(Categoria, pk=pk)
        try:
            categoria.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'No se puede eliminar esta categoría porque tiene productos asociados'
            }, status=400)
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

# Vistas similares para Distribuidores
@login_required
def agregar_distribuidor(request):
    if request.method == 'POST':
        form = DistribuidorForm(request.POST)
        if form.is_valid():
            distribuidor = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Distribuidor agregado correctamente',
                'distribuidor': {
                    'id': distribuidor.id,
                    'nombre': distribuidor.nombre,
                    'cif': distribuidor.cif,
                    'telefono': distribuidor.telefono
                }
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

@login_required
def editar_distribuidor(request, pk):
    distribuidor = get_object_or_404(Distribuidor, pk=pk)
    if request.method == 'POST':
        form = DistribuidorForm(request.POST, instance=distribuidor)
        if form.is_valid():
            distribuidor = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Distribuidor actualizado correctamente',
                'distribuidor': {
                    'id': distribuidor.id,
                    'nombre': distribuidor.nombre,
                    'cif': distribuidor.cif,
                    'telefono': distribuidor.telefono
                }
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

@login_required
def eliminar_distribuidor(request, pk):
    if request.method == 'POST':
        distribuidor = get_object_or_404(Distribuidor, pk=pk)
        try:
            distribuidor.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'No se puede eliminar este distribuidor porque tiene productos asociados'
            }, status=400)
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)




@login_required
def nuevo_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Producto registrado correctamente',
                'producto_id': producto.id
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)

    context = {
        'form': ProductoForm(),
        'categorias': Categoria.objects.all(),
        'distribuidores': Distribuidor.objects.all()
    }
    return render(request, 'inventario/nuevo_producto.html', context)

@login_required
def generar_etiqueta(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    # Generar código de barras
    output = io.BytesIO()
    EAN13(producto.codigo_ean, writer=ImageWriter()).write(output)
    codigo_barras = base64.b64encode(output.getvalue()).decode()

    context = {
        'producto': producto,
        'codigo_barras': codigo_barras
    }
    return render(request, 'inventario/etiqueta_producto.html', context)

@login_required
def almacen(request):
    productos = Producto.objects.select_related('categoria', 'distribuidor').all()
    
    # Búsqueda
    query = request.GET.get('q', '')
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(codigo_ean__icontains=query) |
            Q(categoria__nombre__icontains=query) |
            Q(distribuidor__nombre__icontains=query)
        )

    # Filtros
    categoria = request.GET.get('categoria')
    if categoria:
        productos = productos.filter(categoria_id=categoria)

    # Ordenamiento
    order_by = request.GET.get('order_by', '-fecha_registro')
    productos = productos.order_by(order_by)

    # Paginación
    paginator = Paginator(productos, 10)
    page = request.GET.get('page')
    productos = paginator.get_page(page)

    context = {
        'productos': productos,
        'categorias': Categoria.objects.all()
    }
    return render(request, 'inventario/almacen.html', context)

@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Producto actualizado correctamente'
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
    
    # Para peticiones GET, renderizamos el formulario
    context = {
        'form': ProductoForm(instance=producto),
        'producto': producto,
        'categorias': Categoria.objects.all(),
        'distribuidores': Distribuidor.objects.all()
    }
    return render(request, 'inventario/editar_producto.html', context)

@login_required
def eliminar_producto(request, pk):
    if request.method == 'POST':
        try:
            producto = get_object_or_404(Producto, pk=pk)
            producto.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)