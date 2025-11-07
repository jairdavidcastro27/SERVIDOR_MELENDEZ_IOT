from django.contrib import admin
from .models import *

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('id','nombre','apellido','fecha_registro')
    search_fields=('dni','nombre','apellido')

admin.site.register([Cuidador, Dispositivo, SesionPaciente, DatoSensor, Alerta, ComandoControl, MensajeCuidador])