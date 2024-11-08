# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.authentication.urls')),  # Esta línea es importante
    path('compras/', include('apps.compras.urls')),
    path('ventas/', include('apps.ventas.urls')),
    path('sat/', include('apps.sat.urls')),
    path('inventario/', include('apps.inventario.urls')),
    path('ajustes/', include('apps.ajustes.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)