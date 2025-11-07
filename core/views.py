from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Paciente, SesionPaciente, Dispositivo, Cuidador
from .serializers import SesionSerializer
from rest_framework.decorators import permission_classes

# ==================== LOGIN DEL CUIDADOR ====================
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])  # ← EXCEPCIÓN: NO PIDE TOKEN
def login_cuidador(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Faltan datos o contraseña'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user and hasattr(user, 'cuidador'):
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'cuidador_id': user.cuidador.id,
            'nombre': user.first_name or user.username
        })
    else:
        return Response({'error': 'Credenciales inválidas o no eres cuidador'}, status=status.HTTP_401_UNAUTHORIZED)


# ==================== INICIAR SESIÓN POR DNI ====================
class IniciarSesionDNI(APIView):
    def post(self, request):
        dni = request.data.get('dni')
        cuidador_id = request.data.get('cuidador_id')

        try:
            paciente = Paciente.objects.get(dni=dni)
            cuidador = Cuidador.objects.get(id=cuidador_id)
            dispositivo = Dispositivo.objects.first()

            # Cerrar sesión anterior
            sesion_anterior = SesionPaciente.objects.filter(activa=True).first()
            if sesion_anterior:  # ← CORREGIDO: "session_anterior" → "sesion_anterior"
                sesion_anterior.activa = False
                sesion_anterior.fin = timezone.now()  # ← CORREGIDO: "fecha_fin" → "fin"
                sesion_anterior.save()

            # Nueva sesión
            sesion = SesionPaciente.objects.create(
                paciente=paciente,
                dispositivo=dispositivo,
                cuidador=cuidador,
                activa=True
            )

            # ← CORREGIDO: "Se(sesion).data" → "SesionSerializer(sesion).data"
            return Response(SesionSerializer(sesion).data, status=status.HTTP_201_CREATED)

        except Paciente.DoesNotExist:
            return Response({'error': 'Paciente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Cuidador.DoesNotExist:
            return Response({'error': 'Cuidador no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== PACIENTE ACTUAL ====================
class PacienteActual(APIView):
    def get(self, request):
        sesion = SesionPaciente.objects.filter(activa=True).first()
        if sesion:
            return Response(SesionSerializer(sesion).data)
        return Response({"mensaje": "Nadie está usando los lentes"}, status=200)