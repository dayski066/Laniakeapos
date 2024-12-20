# apps/sat/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.conf import settings
from xhtml2pdf import pisa
from io import BytesIO
import os
import json
import base64
from decimal import Decimal
from .forms import ReparacionForm, DetalleReparacionForm
from .models import Reparacion, DetalleReparacion
from apps.ajustes.models import Cliente
from qrcode import QRCode
import qrcode
from datetime import datetime
from django.db.models import Q

@login_required
def nueva_reparacion(request):
    if request.method == 'POST':
        form = ReparacionForm(request.POST)
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

                # Crear la reparación
                reparacion = form.save(commit=False)
                reparacion.cliente = cliente
                reparacion.usuario = request.user
                reparacion.save()

                # Procesar los dispositivos
                dispositivos = json.loads(request.POST.get('dispositivos', '[]'))
                for dispositivo in dispositivos:
                    precio = Decimal(str(dispositivo['precio']).replace(',', '.'))
                    DetalleReparacion.objects.create(
                        reparacion=reparacion,
                        tipo_dispositivo=dispositivo['tipo_dispositivo'],
                        marca=dispositivo['marca'],
                        modelo=dispositivo['modelo'],
                        numero_serie=dispositivo['numero_serie'],
                        tipo_bloqueo=dispositivo['tipo_bloqueo'],
                        bloqueo=dispositivo['bloqueo'],
                        averia=dispositivo['averia'],
                        precio=precio
                    )
                
                return JsonResponse({
                    'success': True,
                    'message': '¡Reparación registrada con éxito!',
                    'reparacion_id': reparacion.id
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
            
    form = ReparacionForm()
    detalle_form = DetalleReparacionForm()
    return render(request, 'sat/nueva_reparacion.html', {
        'form': form,
        'detalle_form': detalle_form,
        'title': 'Nueva Reparación'
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
def historial_reparaciones(request):
    reparaciones = Reparacion.objects.select_related('cliente').prefetch_related('detalles').all()
    
    # Búsqueda
    query = request.GET.get('q', '')
    if query:
        reparaciones = reparaciones.filter(
            Q(cliente__nombre_completo__icontains=query) |
            Q(cliente__dni__icontains=query) |
            Q(detalles__marca__icontains=query) |
            Q(detalles__modelo__icontains=query) |
            Q(detalles__numero_serie__icontains=query)
        ).distinct()

    # Mantener el ordenamiento por fecha
    reparaciones = reparaciones.order_by('-fecha')

    return render(request, 'sat/historial_reparaciones.html', {
        'reparaciones': reparaciones,
        'title': 'Historial de Reparaciones'
    })

@login_required
def editar_reparacion(request, reparacion_id):
    """Vista para editar reparación"""
    reparacion = get_object_or_404(
        Reparacion.objects.select_related('cliente').prefetch_related('detalles'), 
        id=reparacion_id
    )
    
    if request.method == 'POST':
        form = ReparacionForm(request.POST, instance=reparacion)
        if form.is_valid():
            try:
                # Actualizar datos del cliente
                cliente = reparacion.cliente
                cliente.nombre_completo = form.cleaned_data['nombre_completo']
                cliente.dni = form.cleaned_data['dni']
                cliente.direccion = form.cleaned_data['direccion']
                cliente.telefono = form.cleaned_data['telefono']
                cliente.save()

                # Procesar los dispositivos modificados
                dispositivos_data = json.loads(request.POST.get('dispositivos', '[]'))
                
                # Eliminar los detalles actuales
                reparacion.detalles.all().delete()
                
                # Crear los nuevos detalles
                for dispositivo in dispositivos_data:
                    precio = Decimal(str(dispositivo['precio']).replace(',', '.'))
                    DetalleReparacion.objects.create(
                        reparacion=reparacion,
                        tipo_dispositivo=dispositivo['tipo_dispositivo'],
                        marca=dispositivo['marca'],
                        modelo=dispositivo['modelo'],
                        numero_serie=dispositivo['numero_serie'],
                        tipo_bloqueo=dispositivo['tipo_bloqueo'],
                        bloqueo=dispositivo.get('bloqueo', ''),
                        averia=dispositivo.get('averia', ''),
                        precio=precio
                    )

                reparacion.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Reparación actualizada correctamente'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error al actualizar la reparación: {str(e)}'
                }, status=400)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Formulario inválido',
                'errors': form.errors
            }, status=400)

    # Para GET, preparar formulario
    initial_data = {
        'nombre_completo': reparacion.cliente.nombre_completo,
        'dni': reparacion.cliente.dni,
        'direccion': reparacion.cliente.direccion,
        'telefono': reparacion.cliente.telefono,
    }
    
    form = ReparacionForm(instance=reparacion, initial=initial_data)
    detalle_form = DetalleReparacionForm()
    
    # Obtener detalles usando values() para mejor rendimiento
    detalles_data = list(reparacion.detalles.values(
        'id', 'tipo_dispositivo', 'marca', 'modelo', 
        'numero_serie', 'tipo_bloqueo', 'bloqueo', 
        'averia', 'precio'
    ))

    # Convertir precios a string y manejar valores nulos
    for detalle in detalles_data:
        detalle['precio'] = str(detalle['precio'])
        detalle['bloqueo'] = detalle['bloqueo'] or ''
        detalle['averia'] = detalle['averia'] or ''

    # Convertir a JSON de forma segura
    detalles_json = json.dumps(detalles_data, ensure_ascii=False)

    context = {
        'form': form,
        'detalle_form': detalle_form,
        'detalles_data': detalles_data,
        'reparacion': reparacion,
        'title': f'Editar Reparación #{reparacion.id}'
    }

    return render(request, 'sat/editar_reparacion.html', context)

@login_required
def eliminar_reparacion(request, reparacion_id):
    if request.method == 'POST':
        try:
            reparacion = Reparacion.objects.get(id=reparacion_id)
            reparacion.delete()
            return JsonResponse({'success': True})
        except Reparacion.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Reparación no encontrada'
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
@login_required
def generar_orden_pdf(request, reparacion_id):
    

    # Obtener la reparación con sus relaciones
    reparacion = get_object_or_404(
        Reparacion.objects.select_related('cliente').prefetch_related('detalles'), 
        id=reparacion_id
    )
    
    # Datos de la empresa
    empresa = {
        'nombre': 'LaniaKea Pos',
        'cif': 'B12345678',
        'direccion': 'Calle Principal, 1',
        'cp': '28001',
        'ciudad': 'Madrid'
    }

    # Generar QR
    def generar_qr(datos):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(datos)
        qr.make(fit=True)

        img_qr = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img_qr.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()

    # Datos para el QR
    datos_qr = {
        'id': f"R-{reparacion.id}/{reparacion.fecha.year}",
        'cliente': reparacion.cliente.nombre_completo,
        'telefono': reparacion.cliente.telefono,
        'fecha': reparacion.fecha.strftime('%d/%m/%Y')
    }
    
    # Convertir a string para el QR
    qr_string = '\n'.join([f"{k}: {v}" for k, v in datos_qr.items()])
    qr_code = generar_qr(qr_string)

    # Cargar logo
    logo_path = os.path.join(settings.BASE_DIR, 'apps', 'static', 'assets', 'img', 'logo.png')
    try:
        with open(logo_path, 'rb') as f:
            logo_data = base64.b64encode(f.read()).decode('utf-8')
            logo_base64 = f'data:image/png;base64,{logo_data}'
    except Exception as e:
        print(f"Error al leer el logo: {e}")
        logo_base64 = ''

    # Preparar el contexto
    context = {
        'reparacion': reparacion,
        'cliente': reparacion.cliente,
        'empresa': empresa,
        'logo_base64': logo_base64,
        'fecha': reparacion.fecha.strftime('%d/%m/%Y %H:%M'),
        'qr_code': qr_code,
        'año_actual': datetime.now().year,
        # Añadir información adicional para la etiqueta
        'etiqueta': {
            'id': f"R-{reparacion.id}/{reparacion.fecha.year}",
            'fecha_corta': reparacion.fecha.strftime('%d/%m/%Y'),
            'primer_dispositivo': reparacion.detalles.first() if reparacion.detalles.exists() else None
        }
    }

    # Generar PDF
    template = get_template('sat/orden_pdf.html')
    html = template.render(context)
    result = BytesIO()
    
    # Configuración adicional para mejorar la calidad del PDF
    pdf = pisa.pisaDocument(
        BytesIO(html.encode("UTF-8")), 
        result,
        encoding='utf-8',
        show_error_as_pdf=True,
        link_callback=fetch_resources  # Función que definiremos a continuación
    )
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f'orden_reparacion_{reparacion.id}_{reparacion.fecha.strftime("%Y%m%d")}.pdf'
        response['Content-Disposition'] = f'filename="{filename}"'
        return response
    
    print(f"Error al generar PDF: {pdf.err}")
    return HttpResponse('Error al generar el PDF', status=500)

# Función auxiliar para manejar recursos estáticos
def fetch_resources(uri, rel):
    """
    Callback para manejar URLs en el PDF
    """
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    elif uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    else:
        path = uri

    return path

# Vista
@login_required
def eliminar_detalle_reparacion(request, detalle_id):
    if request.method == 'POST':
        detalle = get_object_or_404(DetalleReparacion, id=detalle_id)
        # Verificar que no es el último dispositivo
        if detalle.reparacion.detalles.count() <= 1:
            return JsonResponse({
                'success': False,
                'message': 'No se puede eliminar el último dispositivo de la reparación'
            }, status=400)
        detalle.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

@login_required
def generar_codigo_qr(texto):
    qr = QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(texto)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir la imagen a base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()