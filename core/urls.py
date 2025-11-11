from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import viewsets

# Crear router para ViewSets
router = DefaultRouter()
router.register(r'pacientes', viewsets.PacienteViewSet)
router.register(r'sesiones', viewsets.SesionViewSet)
router.register(r'dispositivos', viewsets.DispositivoViewSet)
router.register(r'alertas', viewsets.AlertaViewSet)
router.register(r'comandos', viewsets.ComandoControlViewSet)
router.register(r'mensajes', viewsets.MensajeViewSet)
router.register(r'datos', viewsets.DatoSensorViewSet)

urlpatterns = [
    # Autenticación y endpoints existentes
    path('login/', views.login_cuidador),
    path('iniciar-sesion/', views.IniciarSesionDNI.as_view()),
    path('paciente-actual/', views.PacienteActual.as_view()),
    path('telemetria/', views.recibir_telemetria),
    
    # Incluir todas las URLs del router
    path('', include(router.urls)),
]