from django.urls import path
from . import views

urlpatterns = [
# LOGIN DEL CUIDADOR
    path('login/', views.login_cuidador),

    # ACTIVAR PACIENTE POR DNI
    path('iniciar-sesion/', views.IniciarSesionDNI.as_view()),

    # VER QUIÉN USA LOS LENTES
    path('paciente-actual/', views.PacienteActual.as_view()),
]