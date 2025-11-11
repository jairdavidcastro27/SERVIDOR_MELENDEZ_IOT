from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Paciente, SesionPaciente, Dispositivo, DatoSensor, Alerta, ComandoControl, MensajeCuidador

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'

class DispositivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispositivo
        fields = '__all__'

class SesionSerializer(serializers.ModelSerializer):
    paciente = PacienteSerializer(read_only=True)
    paciente_nombre = serializers.CharField(source='paciente.nombre', read_only=True)
    cuidador_nombre = serializers.CharField(source='cuidador.user.username', read_only=True)
    
    class Meta:
        model = SesionPaciente
        fields = '__all__'

class DatoSensorSerializer(serializers.ModelSerializer):
    timestamp_local = serializers.SerializerMethodField()
    
    class Meta:
        model = DatoSensor
        fields = ['id', 'sesion', 'color', 'temperatura', 'distancia', 'nivel', 'timestamp', 'timestamp_local']
        
    def get_timestamp_local(self, obj):
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')

class AlertaSerializer(serializers.ModelSerializer):
    sesion_info = SesionSerializer(source='sesion', read_only=True)
    
    class Meta:
        model = Alerta
        fields = '__all__'

class ComandoControlSerializer(serializers.ModelSerializer):
    sesion_info = SesionSerializer(source='sesion', read_only=True)
    
    class Meta:
        model = ComandoControl
        fields = '__all__'

class MensajeCuidadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = MensajeCuidador
        fields = ['id', 'mensaje', 'leido', 'timestamp']
        read_only_fields = ['leido', 'timestamp']