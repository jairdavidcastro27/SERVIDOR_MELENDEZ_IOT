from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import models  # Agregamos esta importación para las funciones de agregación
from .models import (
    Paciente, SesionPaciente, Dispositivo, DatoSensor,
    Alerta, ComandoControl, MensajeCuidador
)
from .serializers import (
    PacienteSerializer, SesionSerializer, DispositivoSerializer,
    DatoSensorSerializer, AlertaSerializer, ComandoControlSerializer,
    MensajeCuidadorSerializer
)

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Si quieres filtrar por cuidador más adelante
        return Paciente.objects.all()

class SesionViewSet(viewsets.ModelViewSet):
    queryset = SesionPaciente.objects.all()
    serializer_class = SesionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def finalizar_activa(self, request):
        sesion = SesionPaciente.objects.filter(activa=True).first()
        if sesion:
            sesion.activa = False
            sesion.fin = timezone.now()
            sesion.save()
            return Response(SesionSerializer(sesion).data)
        return Response(
            {"error": "No hay sesión activa"},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True, methods=['get'])
    def datos(self, request, pk=None):
        """
        Obtiene los datos de una sesión específica.
        Parámetros de consulta opcionales:
        - start_time: Timestamp inicial (formato ISO)
        - end_time: Timestamp final (formato ISO)
        - limit: Número máximo de registros (default: 1000)
        """
        sesion = self.get_object()
        
        # Obtener parámetros de consulta
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        limit = int(request.query_params.get('limit', 1000))
        
        # Construir query base
        datos = DatoSensor.objects.filter(sesion=sesion)
        
        # Aplicar filtros de tiempo si se proporcionan
        if start_time:
            datos = datos.filter(timestamp__gte=start_time)
        if end_time:
            datos = datos.filter(timestamp__lte=end_time)
            
        # Ordenar por timestamp y limitar resultados
        datos = datos.order_by('-timestamp')[:limit]
        
        serializer = DatoSensorSerializer(datos, many=True)
        return Response({
            'sesion_id': sesion.id,
            'paciente': sesion.paciente.nombre,
            'total_registros': datos.count(),
            'datos': serializer.data
        })

    @action(detail=True, methods=['get'])
    def estadisticas(self, request, pk=None):
        """
        Obtiene estadísticas básicas de los datos de la sesión
        """
        sesion = self.get_object()
        datos = DatoSensor.objects.filter(sesion=sesion)
        
        if not datos.exists():
            return Response({
                'error': 'No hay datos para esta sesión'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Calcular estadísticas
        stats = {
            'temperatura': {
                'min': datos.aggregate(models.Min('temperatura'))['temperatura__min'],
                'max': datos.aggregate(models.Max('temperatura'))['temperatura__max'],
                'avg': datos.aggregate(models.Avg('temperatura'))['temperatura__avg']
            },
            'distancia': {
                'min': datos.aggregate(models.Min('distancia'))['distancia__min'],
                'max': datos.aggregate(models.Max('distancia'))['distancia__max'],
                'avg': datos.aggregate(models.Avg('distancia'))['distancia__avg']
            },
            'total_registros': datos.count(),
            'duracion_minutos': (datos.latest('timestamp').timestamp - 
                               datos.earliest('timestamp').timestamp).total_seconds() / 60
        }
        
        return Response(stats)

class DispositivoViewSet(viewsets.ModelViewSet):
    queryset = Dispositivo.objects.all()
    serializer_class = DispositivoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def actualizar_estado(self, request, pk=None):
        dispositivo = self.get_object()
        nuevo_estado = request.data.get('estado')
        if nuevo_estado in ['ACTIVO', 'INACTIVO']:
            dispositivo.estado = nuevo_estado
            dispositivo.ultima_conexion = timezone.now()
            dispositivo.save()
            return Response(DispositivoSerializer(dispositivo).data)
        return Response(
            {"error": "Estado inválido"},
            status=status.HTTP_400_BAD_REQUEST
        )

class AlertaViewSet(viewsets.ModelViewSet):
    queryset = Alerta.objects.all()
    serializer_class = AlertaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Alerta.objects.filter(vista=False).order_by('-timestamp')

    @action(detail=True, methods=['post'])
    def marcar_vista(self, request, pk=None):
        alerta = self.get_object()
        alerta.vista = True
        alerta.save()
        return Response(AlertaSerializer(alerta).data)

class ComandoControlViewSet(viewsets.ModelViewSet):
    queryset = ComandoControl.objects.all()
    serializer_class = ComandoControlSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        comandos = ComandoControl.objects.filter(ejecutado=False)
        serializer = ComandoControlSerializer(comandos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def marcar_ejecutado(self, request, pk=None):
        comando = self.get_object()
        comando.ejecutado = True
        comando.save()
        return Response(ComandoControlSerializer(comando).data)

class MensajeViewSet(viewsets.ModelViewSet):
    queryset = MensajeCuidador.objects.all()
    serializer_class = MensajeCuidadorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MensajeCuidador.objects.filter(
            cuidador__user=self.request.user
        ).order_by('-timestamp')

    def perform_create(self, serializer):
        # Obtener sesión activa
        sesion_activa = SesionPaciente.objects.filter(activa=True).first()
        if not sesion_activa:
            raise serializers.ValidationError("No hay sesión activa para enviar el mensaje.")
        
        # Guardar mensaje
        serializer.save(
            cuidador=self.request.user.cuidador,
            sesion=sesion_activa
        )

    @action(detail=True, methods=['post'])
    def marcar_leido(self, request, pk=None):
        mensaje = self.get_object()
        mensaje.leido = True
        mensaje.save()
        return Response(MensajeCuidadorSerializer(mensaje).data)

class DatoSensorViewSet(viewsets.ModelViewSet):
    queryset = DatoSensor.objects.all()
    serializer_class = DatoSensorSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def ultimos(self, request):
        sesion_activa = SesionPaciente.objects.filter(activa=True).first()
        if not sesion_activa:
            return Response(
                {"error": "No hay sesión activa"},
                status=status.HTTP_404_NOT_FOUND
            )
        datos = DatoSensor.objects.filter(
            sesion=sesion_activa
        ).order_by('-timestamp')[:10]
        serializer = DatoSensorSerializer(datos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def historico(self, request):
        sesion_id = request.query_params.get('sesion')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        datos = DatoSensor.objects.all()
        if sesion_id:
            datos = datos.filter(sesion_id=sesion_id)
        if fecha_inicio:
            datos = datos.filter(timestamp__gte=fecha_inicio)
        if fecha_fin:
            datos = datos.filter(timestamp__lte=fecha_fin)
            
        datos = datos.order_by('-timestamp')
        serializer = DatoSensorSerializer(datos, many=True)
        return Response(serializer.data)