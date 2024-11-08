# apps/ventas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.contrib import messages
from xhtml2pdf import pisa
import os
import json
import base64
from decimal import Decimal
from datetime import datetime
from .forms import VentaForm, DetalleVentaForm
from .models import Venta, DetalleVenta
from apps.ajustes.models import Cliente
from django.conf import settings

@login_required
def nueva_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
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

                # Crear la venta
                venta = form.save(commit=False)
                venta.cliente = cliente
                venta.usuario = request.user
                venta.save()

                # Procesar los dispositivos
                dispositivos = json.loads(request.POST.get('dispositivos', '[]'))
                for dispositivo in dispositivos:
                    precio = Decimal(str(dispositivo['precio']).replace(',', '.'))
                    DetalleVenta.objects.create(
                        venta=venta,
                        tipo_dispositivo=dispositivo['tipo_dispositivo'],
                        marca=dispositivo['marca'],
                        modelo=dispositivo['modelo'],
                        numero_serie=dispositivo['numero_serie'],
                        estado=dispositivo['estado'],
                        precio=precio,
                        nota=dispositivo.get('nota', '')
                    )
                
                return JsonResponse({
                    'success': True,
                    'message': '¡Venta registrada con éxito!',
                    'venta_id': venta.id
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
            
    form = VentaForm()
    detalle_form = DetalleVentaForm()
    return render(request, 'ventas/nueva_venta.html', {
        'form': form,
        'detalle_form': detalle_form,
        'title': 'Nueva Venta'
    })

@login_required
def agregar_detalle_venta(request):
    if request.method == 'POST':
        form = DetalleVentaForm(request.POST)
        if form.is_valid():
            detalle = form.save()
            return JsonResponse({
                'success': True,
                'detalle': {
                    'id': detalle.id,
                    'tipo_dispositivo': detalle.get_tipo_dispositivo_display(),
                    'marca': detalle.marca,
                    'modelo': detalle.modelo,
                    'numero_serie': detalle.numero_serie,
                    'estado': detalle.get_estado_display(),
                    'precio': str(detalle.precio)
                }
            })
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@login_required
def eliminar_detalle_venta(request, detalle_id):
    if request.method == 'POST':
        detalle = get_object_or_404(DetalleVenta, id=detalle_id)
        # Verificar que no es el último dispositivo
        if detalle.venta.detalles.count() <= 1:
            return JsonResponse({
                'success': False,
                'message': 'No se puede eliminar el último dispositivo de la venta'
            }, status=400)
        detalle.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

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
def historial_ventas(request):
    ventas = Venta.objects.select_related('cliente').prefetch_related('detalles').all().order_by('-fecha')
    # Añadir el total calculado a cada venta
    for venta in ventas:
        venta.total_calculado = sum(Decimal(str(detalle.precio)) for detalle in venta.detalles.all())
    return render(request, 'ventas/historial_ventas.html', {
        'ventas': ventas,
        'title': 'Historial de Ventas'
    })


@login_required
def generar_factura_pdf(request, venta_id):
    try:
        venta = Venta.objects.select_related('cliente').prefetch_related('detalles').get(id=venta_id)
        detalles = venta.detalles.all()
        
        # Calcular totales usando Decimal
        subtotal = sum(Decimal(str(detalle.precio)) for detalle in detalles)
        iva_rate = Decimal('0.21')  # 21% IVA
        
        # Calcular base imponible (subtotal sin IVA)
        base_imponible = (subtotal / (Decimal('1') + iva_rate)).quantize(Decimal('0.01'))
        
        # Calcular IVA
        iva = (subtotal - base_imponible).quantize(Decimal('0.01'))
        
        # Total es la suma de base imponible + IVA
        total = subtotal.quantize(Decimal('0.01'))
        
        # Generar número de factura en formato DDMMYY-ID
        numero_factura = f"{venta.fecha.strftime('%d%m%y')}-{venta.id}"
        
        # Cargar logo
        logo_path = os.path.join(settings.BASE_DIR, 'apps', 'static', 'assets', 'img', 'logo.png')
        try:
            with open(logo_path, 'rb') as f:
                logo_data = base64.b64encode(f.read()).decode('utf-8')
                logo_base64 = f'data:image/png;base64,{logo_data}'
        except Exception as e:
            print(f"Error al leer el logo: {e}")
            logo_base64 = ''
        
        context = {
            'venta': venta,
            'detalles': detalles,
            'fecha': venta.fecha.strftime('%d de %B de %Y'),
            'numero_factura': numero_factura,
            'empresa': {
                'nombre': 'La Tienda Del Móvil',
                'cif': 'B12345678',
                'direccion': 'Avenida Ramón y Cajal, 5b',
                'ciudad': 'Madrid',
                'cp': '28001'
            },
            'logo_base64': logo_base64,
            'cliente': venta.cliente,
            'base_imponible': base_imponible,
            'iva': iva,
            'total': total
        }
        
        template = get_template('ventas/factura_pdf.html')
        html = template.render(context)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{numero_factura}.pdf"'
        
        pisa.CreatePDF(html, dest=response, encoding='utf-8')
        
        return response
    except Venta.DoesNotExist:
        return HttpResponse('Venta no encontrada', status=404)
    except Exception as e:
        return HttpResponse(f'Error al generar la factura: {str(e)}', status=500)
    
    
@login_required
def editar_venta(request, venta_id):
    venta = get_object_or_404(Venta.objects.select_related('cliente').prefetch_related('detalles'), id=venta_id)
    
    if request.method == 'POST':
        form = VentaForm(request.POST, instance=venta)
        if form.is_valid():
            try:
                # Procesar datos del cliente
                cliente, created = Cliente.objects.update_or_create(
                    dni=form.cleaned_data['dni'],
                    defaults={
                        'nombre_completo': form.cleaned_data['nombre_completo'],
                        'direccion': form.cleaned_data['direccion'],
                        'telefono': form.cleaned_data['telefono']
                    }
                )

                venta = form.save(commit=False)
                venta.cliente = cliente
                venta.save()

                # Procesar los dispositivos actualizados
                dispositivos_nuevos = json.loads(request.POST.get('dispositivos', '[]'))
                
                # Eliminar dispositivos que ya no están en la lista
                ids_actuales = [d.get('id') for d in dispositivos_nuevos if d.get('id')]
                venta.detalles.exclude(id__in=ids_actuales).delete()
                
                # Actualizar o crear nuevos dispositivos
                for dispositivo in dispositivos_nuevos:
                    precio = Decimal(str(dispositivo['precio']).replace(',', '.'))
                    if dispositivo.get('id'):
                        DetalleVenta.objects.filter(id=dispositivo['id']).update(
                            tipo_dispositivo=dispositivo['tipo_dispositivo'],
                            marca=dispositivo['marca'],
                            modelo=dispositivo['modelo'],
                            numero_serie=dispositivo['numero_serie'],
                            estado=dispositivo['estado'],
                            precio=precio,
                            nota=dispositivo.get('nota', '')
                        )
                    else:
                        DetalleVenta.objects.create(
                            venta=venta,
                            tipo_dispositivo=dispositivo['tipo_dispositivo'],
                            marca=dispositivo['marca'],
                            modelo=dispositivo['modelo'],
                            numero_serie=dispositivo['numero_serie'],
                            estado=dispositivo['estado'],
                            precio=precio,
                            nota=dispositivo.get('nota', '')
                        )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Venta actualizada correctamente'
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

    # Para GET request
    initial_data = {
        'nombre_completo': venta.cliente.nombre_completo,
        'dni': venta.cliente.dni,
        'direccion': venta.cliente.direccion,
        'telefono': venta.cliente.telefono,
        'nota': venta.nota
    }
    
    form = VentaForm(instance=venta, initial=initial_data)
    detalle_form = DetalleVentaForm()
    
    # Preparar los detalles para el template
    detalles_json = json.dumps([{
        'id': detalle.id,
        'tipo_dispositivo': detalle.tipo_dispositivo,
        'marca': detalle.marca,
        'modelo': detalle.modelo,
        'numero_serie': detalle.numero_serie,
        'estado': detalle.estado,
        'precio': str(detalle.precio),
        'nota': detalle.nota or ''
    } for detalle in venta.detalles.all()])
    
    return render(request, 'ventas/editar_venta.html', {
        'form': form,
        'detalle_form': detalle_form,
        'venta': venta,
        'detalles_json': detalles_json,
        'title': 'Editar Venta'
    })

@login_required
def editar_detalle_venta(request, detalle_id):
    if request.method == 'POST':
        detalle = get_object_or_404(DetalleVenta, id=detalle_id)
        try:
            data = request.POST
            detalle.tipo_dispositivo = data.get('tipo_dispositivo')
            detalle.marca = data.get('marca')
            detalle.modelo = data.get('modelo')
            detalle.numero_serie = data.get('numero_serie')
            detalle.estado = data.get('estado')
            detalle.precio = Decimal(str(data.get('precio')).replace(',', '.'))
            detalle.nota = data.get('nota', '')
            detalle.save()

            return JsonResponse({
                'success': True,
                'detalle': {
                    'id': detalle.id,
                    'tipo_dispositivo': detalle.tipo_dispositivo,
                    'marca': detalle.marca,
                    'modelo': detalle.modelo,
                    'numero_serie': detalle.numero_serie,
                    'estado': detalle.estado,
                    'precio': str(detalle.precio),
                    'nota': detalle.nota or ''
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)

@login_required
def eliminar_venta(request, venta_id):
    if request.method == 'POST':
        try:
            venta = Venta.objects.get(id=venta_id)
            venta.delete()
            return JsonResponse({'success': True})
        except Venta.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Venta no encontrada'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    }, status=405)

@login_required
def obtener_venta(request, venta_id):
    try:
        venta = Venta.objects.select_related('cliente').prefetch_related('detalles').get(id=venta_id)
        return JsonResponse({
            'success': True,
            'data': {
                'cliente': {
                    'nombre_completo': venta.cliente.nombre_completo,
                    'dni': venta.cliente.dni,
                    'direccion': venta.cliente.direccion,
                    'telefono': venta.cliente.telefono
                },
                'detalles': [{
                    'tipo_dispositivo': detalle.tipo_dispositivo,
                    'marca': detalle.marca,
                    'modelo': detalle.modelo,
                    'numero_serie': detalle.numero_serie,
                    'estado': detalle.estado,
                    'precio': str(detalle.precio),
                    'nota': detalle.nota
                } for detalle in venta.detalles.all()]
            }
        })
    except Venta.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Venta no encontrada'
        }, status=404)