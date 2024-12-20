# apps/compras/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.contrib import messages
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings
import os
import base64
from datetime import datetime
from .forms import CompraForm
from .models import Compra
from apps.ajustes.models import Cliente
from django.db.models import Q

@login_required
def nueva_compra(request):
    if request.method == 'POST':
        form = CompraForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Procesar datos del cliente
                dni = form.cleaned_data['dni']
                cliente, created = Cliente.objects.get_or_create(
                    dni=dni,
                    defaults={
                        'nombre_completo': form.cleaned_data['nombre_completo'],
                        'direccion': form.cleaned_data['direccion'],
                        'telefono': form.cleaned_data['telefono']
                    }
                )

                # Crear la compra
                compra = form.save(commit=False)
                compra.cliente = cliente
                compra.usuario = request.user
                compra.save()
                
                return JsonResponse({
                    'success': True,
                    'message': '¡Compra registrada con éxito!',
                    'compra_id': compra.id
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=400)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Formulario inválido',
                'errors': form.errors
            }, status=400)
            
    form = CompraForm()
    return render(request, 'compras/nueva_compra.html', {
        'form': form,
        'title': 'Nueva Compra'
    })

@login_required
def verificar_dni(request):
    dni = request.GET.get('dni', '')
    try:
        cliente = Cliente.objects.get(dni=dni)
        return JsonResponse({
            'exists': True,
            'data': {
                'nombre_completo': cliente.nombre_completo,
                'direccion': cliente.direccion,
                'telefono': cliente.telefono
            }
        })
    except Cliente.DoesNotExist:
        return JsonResponse({'exists': False})

@login_required
def generar_contrato_pdf(request, compra_id):
    try:
        compra = Compra.objects.select_related('cliente').get(id=compra_id)
        
        # Debug: Verificar datos del cliente
        print("Datos del cliente:")
        print("Nombre:", compra.cliente.nombre_completo)
        print("DNI:", compra.cliente.dni)
        print("Dirección:", compra.cliente.direccion)
        
        # Debug: Verificar ruta del logo
        logo_path = os.path.join(settings.BASE_DIR, 'apps', 'static', 'assets', 'img', 'logo.png')
        print("Ruta del logo:", logo_path)
        print("¿El archivo existe?:", os.path.exists(logo_path))
        
        # Convertir logo a base64
        try:
            with open(logo_path, 'rb') as f:
                logo_data = base64.b64encode(f.read()).decode('utf-8')
                logo_base64 = f'data:image/png;base64,{logo_data}'
                print("Logo codificado correctamente")
        except Exception as e:
            print(f"Error al leer el logo: {e}")
            logo_base64 = ''
        
        context = {
            'compra': compra,
            'cliente': {
                'nombre_completo': compra.cliente.nombre_completo,
                'dni': compra.cliente.dni,
                'direccion': compra.cliente.direccion,
                'telefono': compra.cliente.telefono
            },
            'dispositivo': {
                'tipo': compra.get_tipo_dispositivo_display(),
                'marca': compra.marca,
                'modelo': compra.modelo,
                'numero_serie': compra.numero_serie,
                'estado': compra.get_estado_display(),
                'precio': compra.precio
            },
            'fecha': compra.fecha.strftime('%d de %B de %Y'),
            'empresa': {
                'nombre': 'La Tienda Del Móvil',
                'cif': 'B12345678',
                'direccion': 'Avenida Ramón y Cajal, 5b',
                'ciudad': 'Madrid',
                'cp': '28001'
            },
            'logo_base64': logo_base64,
            'MEDIA_ROOT': settings.MEDIA_ROOT,
        }
        
        template = get_template('compras/contrato_pdf.html')
        html = template.render(context)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="contrato_compra_{compra.id}.pdf"'
        
        def fetch_resources(uri, rel):
            if uri.startswith('data:image/'):
                return uri
            elif uri.startswith(settings.MEDIA_URL):
                path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
            else:
                path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
            return path
        
        pdf_status = pisa.CreatePDF(
            html, 
            dest=response,
            encoding='utf-8',
            link_callback=fetch_resources
        )
        
        if pdf_status.err:
            print("Error al generar PDF:", pdf_status.err)
            return HttpResponse('Error al generar el PDF', status=500)
        
        return response
        
    except Compra.DoesNotExist:
        print(f"No se encontró la compra con ID: {compra_id}")
        return HttpResponse('Compra no encontrada', status=404)
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return HttpResponse('Error al generar el contrato', status=500)

@login_required
def historial_compras(request):
    compras = Compra.objects.select_related('cliente').all()
    
    # Búsqueda
    query = request.GET.get('q', '')
    if query:
        compras = compras.filter(
            Q(cliente__nombre_completo__icontains=query) |
            Q(cliente__dni__icontains=query) |
            Q(marca__icontains=query) |
            Q(modelo__icontains=query) |
            Q(numero_serie__icontains=query)
        ).distinct()

    # Mantener el ordenamiento por fecha
    compras = compras.order_by('-fecha')

    return render(request, 'compras/historial_compras.html', {
        'compras': compras,
        'title': 'Historial de Compras'
    })

@login_required
def editar_compra(request, compra_id):
    compra = get_object_or_404(Compra.objects.select_related('cliente'), id=compra_id)
    
    if request.method == 'POST':
        form = CompraForm(request.POST, request.FILES, instance=compra)
        if form.is_valid():
            try:
                # Actualizar cliente
                cliente, created = Cliente.objects.update_or_create(
                    dni=form.cleaned_data['dni'],
                    defaults={
                        'nombre_completo': form.cleaned_data['nombre_completo'],
                        'direccion': form.cleaned_data['direccion'],
                        'telefono': form.cleaned_data['telefono']
                    }
                )

                compra = form.save(commit=False)
                compra.cliente = cliente
                
                # Manejar la imagen del DNI
                if 'imagen_dni' in request.FILES:
                    # Si hay una imagen anterior, eliminarla
                    if compra.imagen_dni:
                        try:
                            os.remove(compra.imagen_dni.path)
                        except Exception as e:
                            print(f"Error eliminando imagen anterior: {e}")
                else:
                    # Si no se subió nueva imagen, mantener la anterior
                    compra.imagen_dni = Compra.objects.get(id=compra_id).imagen_dni
                
                compra.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Compra actualizada correctamente',
                    'data': {
                        'id': compra.id,
                        'fecha': compra.fecha.strftime('%d/%m/%Y %H:%M'),
                        'cliente_nombre': compra.cliente.nombre_completo,
                        'cliente_dni': compra.cliente.dni,
                        'dispositivo': f"{compra.marca} {compra.modelo}",
                        'numero_serie': compra.numero_serie,
                        'estado': compra.get_estado_display(),
                        'precio': str(compra.precio)
                    }
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=400)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Formulario inválido',
                'errors': form.errors
            }, status=400)

@login_required
def obtener_compra(request, compra_id):
    try:
        compra = Compra.objects.select_related('cliente').get(id=compra_id)
        data = {
            'success': True,
            'data': {
                'cliente': {
                    'nombre_completo': compra.cliente.nombre_completo,
                    'dni': compra.cliente.dni,
                    'direccion': compra.cliente.direccion,
                    'telefono': compra.cliente.telefono
                },
                'dispositivo': {
                    'tipo': compra.tipo_dispositivo,
                    'marca': compra.marca,
                    'modelo': compra.modelo,
                    'numero_serie': compra.numero_serie,
                    'estado': compra.estado,
                    'precio': str(compra.precio),
                    'nota': compra.nota
                },
                'imagen_dni_url': compra.imagen_dni.url if compra.imagen_dni else None
            }
        }
        return JsonResponse(data)
    except Compra.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Compra no encontrada'
        }, status=404)

@login_required
def eliminar_compra(request, compra_id):
    if request.method == 'POST':
        try:
            compra = Compra.objects.select_related('cliente').get(id=compra_id)
            # Intentar eliminar la imagen del DNI si existe
            if compra.imagen_dni:
                try:
                    if os.path.isfile(compra.imagen_dni.path):
                        os.remove(compra.imagen_dni.path)
                except Exception as e:
                    print(f"Error al eliminar imagen: {e}")
            compra.delete()
            return JsonResponse({'success': True})
        except Compra.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Compra no encontrada'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
