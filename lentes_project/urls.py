from django.contrib import admin
from django.urls import path, include
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('core.urls')),
    
    # Páginas web
    path('', core_views.login_cuidador_view, name='home'),  # Página principal
    path('login_cuidador/', core_views.login_cuidador_view, name='login_cuidador'),
    path('login_paciente/', core_views.login_paciente_view, name='login_paciente'),
    path('monitor/', core_views.monitor_realtime, name='monitor'),
    path('pacientes/', core_views.pacientes_view, name='pacientes'),
    path('sesiones/', core_views.sesiones_view, name='sesiones'),
    path('alertas/', core_views.alertas_view, name='alertas'),
]
