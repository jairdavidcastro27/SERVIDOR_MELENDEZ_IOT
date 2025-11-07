from rest_framework import serializers
from .models import *

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'

class SesionSerializer(serializers.ModelSerializer):
    paciente = PacienteSerializer()
    class Meta:
        model = SesionPaciente
        fields = '__all__'

class DatoSensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatoSensor
        fields = '__all__'
