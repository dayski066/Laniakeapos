# apps/sat/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
import os
import json
import base64
from decimal import Decimal
from datetime import datetime
from django.core.serializers.json import DjangoJSONEncoder
from .forms import ReparacionForm, DetalleReparacionForm
from .models import Reparacion, DetalleReparacion
from apps.ajustes.models import Cliente

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
    reparaciones = Reparacion.objects.select_related('cliente').prefetch_related('detalles').all().order_by('-fecha')
    return render(request, 'sat/historial_reparaciones.html', {
        'reparaciones': reparaciones,
        'title': 'Historial de Reparaciones'
    })

@login_required
def editar_reparacion(request, reparacion_id):
  # Obtener la reparación por ID
  reparacion = get_object_or_404(Reparacion, id=reparacion_id)
  
  if request.method == 'POST':
      # Procesar el formulario enviado
      form = ReparacionForm(request.POST, instance=reparacion)
      if form.is_valid():
          # Guardar los cambios
          form.save()
          return JsonResponse({'success': True, 'message': 'Reparación actualizada correctamente'})
  else:
      # Preparar el formulario con los datos existentes
      initial_data = {
          'nombre_completo': reparacion.cliente.nombre_completo,
          'dni': reparacion.cliente.dni,
          'direccion': reparacion.cliente.direccion,
          'telefono': reparacion.cliente.telefono,
      }
      form = ReparacionForm(instance=reparacion, initial=initial_data)

      # Cargar detalles de la reparación
      detalles = []
      for detalle in reparacion.detalles.all():
          detalles.append({
              'id': detalle.id,
              'tipo_dispositivo': detalle.tipo_dispositivo,
              'marca': detalle.marca,
              'modelo': detalle.modelo,
              'numero_serie': detalle.numero_serie,
              'tipo_bloqueo': detalle.tipo_bloqueo,
              'bloqueo': detalle.bloqueo,
              'precio': str(detalle.precio),
              'averia': detalle.averia
          })

      # Convertir detalles a JSON
      detalles_json = json.dumps(detalles, cls=DjangoJSONEncoder)

      # Renderizar el template
      return render(request, 'sat/editar_reparacion.html', {
          'form': form,
          'detalles_json': detalles_json,
          'reparacion': reparacion
      })

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
def obtener_reparacion(request, reparacion_id):
  try:
      reparacion = get_object_or_404(
          Reparacion.objects.select_related('cliente').prefetch_related('detalles'),
          id=reparacion_id
      )
      
      detalles_data = [{
          'id': detalle.id,
          'tipo_dispositivo': detalle.tipo_dispositivo,
          'marca': detalle.marca,
          'modelo': detalle.modelo,
          'numero_serie': detalle.numero_serie,
          'tipo_bloqueo': detalle.tipo_bloqueo,
          'bloqueo': detalle.bloqueo,
          'averia': detalle.averia,
          'precio': str(detalle.precio)
      } for detalle in reparacion.detalles.all()]
      
      return JsonResponse({
          'success': True,
          'reparacion': {
              'cliente': {
                  'dni': reparacion.cliente.dni,
                  'nombre_completo': reparacion.cliente.nombre_completo,
                  'direccion': reparacion.cliente.direccion,
                  'telefono': reparacion.cliente.telefono
              },
              'detalles': detalles_data,
              'total': str(sum(detalle.precio for detalle in reparacion.detalles.all()))
          }
      })
  except Exception as e:
      return JsonResponse({
          'success': False,
          'message': str(e)
      }, status=400)
    
@login_required
def agregar_detalle_reparacion(request):
    if request.method == 'POST':
        form = DetalleReparacionForm(request.POST)
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
                    'tipo_bloqueo': detalle.get_bloqueo_display(),
                    'bloqueo': detalle.bloqueo,
                    'precio': str(detalle.precio)
                }
            })
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@login_required
def editar_detalle_reparacion(request, detalle_id):
    detalle = get_object_or_404(DetalleReparacion, id=detalle_id)
    
    if request.method == 'POST':
        form = DetalleReparacionForm(request.POST, instance=detalle)
        if form.is_valid():
            detalle = form.save()
            return JsonResponse({
                'success': True,
                'detalle': {
                    'id': detalle.id,
                    'tipo_dispositivo': detalle.tipo_dispositivo,
                    'marca': detalle.marca,
                    'modelo': detalle.modelo,
                    'numero_serie': detalle.numero_serie,
                    'tipo_bloqueo': detalle.tipo_bloqueo,
                    'bloqueo': detalle.bloqueo,
                    'averia': detalle.averia,
                    'precio': str(detalle.precio)
                }
            })
        return JsonResponse({
            'success': False, 
            'errors': form.errors
        }, status=400)
    
    # Para peticiones GET, devolver los datos del detalle
    elif request.method == 'GET':
        return JsonResponse({
            'success': True,
            'detalle': {
                'id': detalle.id,
                'tipo_dispositivo': detalle.tipo_dispositivo,
                'marca': detalle.marca,
                'modelo': detalle.modelo,
                'numero_serie': detalle.numero_serie,
                'tipo_bloqueo': detalle.tipo_bloqueo,
                'bloqueo': detalle.bloqueo,
                'averia': detalle.averia,
                'precio': str(detalle.precio)
            }
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)


@login_required
def eliminar_detalle_reparacion(request, detalle_id):
    if request.method == 'POST':
        detalle = get_object_or_404(DetalleReparacion, id=detalle_id)
        if detalle.reparacion.detalles.count() <= 1:
            return JsonResponse({
                'success': False,
                'message': 'No se puede eliminar el único dispositivo de la reparación'
            }, status=400)
        detalle.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=405)

@login_required
def generar_orden_pdf(request, reparacion_id):
    # Obtener la reparación
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

    # Preparar el logo
    logo_path = os.path.join(settings.BASE_DIR, 'apps', 'static', 'assets', 'img', 'logo.png')
    try:
        with open(logo_path, 'rb') as f:
            logo_data = base64.b64encode(f.read()).decode('utf-8')
            logo_base64 = f'data:image/png;base64,{logo_data}'
    except Exception as e:
        print(f"Error al leer el logo: {e}")
        logo_base64 = ''

    # Contexto para el template
    context = {
        'reparacion': reparacion,
        'cliente': reparacion.cliente,
        'empresa': empresa,
        'logo_base64': logo_base64,
        'fecha': reparacion.fecha.strftime('%d/%m/%Y %H:%M')
    }

    # Renderizar el template
    template = get_template('sat/orden_pdf.html')
    html = template.render(context)

    # Crear el PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(
        BytesIO(html.encode("UTF-8")), 
        result,
        encoding='utf-8',
        show_error_as_pdf=True
    )
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'filename="orden_reparacion_{reparacion_id}.pdf"'
        return response
    
    print(f"Error al generar PDF: {pdf.err}")
    return HttpResponse('Error al generar el PDF', status=500)



@login_required
def obtener_detalles_reparacion(request, reparacion_id):
  try:
      reparacion = get_object_or_404(
          Reparacion.objects.prefetch_related('detalles'),
          id=reparacion_id
      )
      
      # Obtener todos los detalles de la reparación
      detalles = reparacion.detalles.all()
      
      # Formatear los detalles para JSON
      detalles_data = [{
          'id': detalle.id,
          'tipo_dispositivo': detalle.tipo_dispositivo,
          'marca': detalle.marca,
          'modelo': detalle.modelo,
          'numero_serie': detalle.numero_serie,
          'tipo_bloqueo': detalle.tipo_bloqueo,
          'bloqueo': detalle.bloqueo,
          'averia': detalle.averia,
          'precio': str(detalle.precio)
      } for detalle in detalles]
      
      return JsonResponse({
          'success': True,
          'detalles': detalles_data,
          'total': str(sum(detalle.precio for detalle in detalles))
      })
      
  except Exception as e:
      return JsonResponse({
          'success': False,
          'message': str(e)
      }, status=400)
  


@login_required
def cargar_detalle_reparacion(request, detalle_id):
    try:
        detalle = get_object_or_404(DetalleReparacion, id=detalle_id)
        
        return JsonResponse({
            'success': True,
            'detalle': {
                'id': detalle.id,
                'tipo_dispositivo': detalle.tipo_dispositivo,
                'marca': detalle.marca,
                'modelo': detalle.modelo,
                'numero_serie': detalle.numero_serie,
                'tipo_bloqueo': detalle.tipo_bloqueo,
                'bloqueo': detalle.bloqueo,
                'averia': detalle.averia,
                'precio': str(detalle.precio)
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
