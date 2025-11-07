import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import datosensor, sesionpaciente

class DatosRealtimeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.task = None
        self.enviar_datos()

    async def disconnect(self, close_code):
        pass
    def enviar_datos(self):
        sesion = SesionPaciente.objects.filter(activa=True).first()
        if sesion:
            ultimo = DatoSensor.objects.filter(sesion=sesion).last()
            if ultimo:
                datos = {
                    'color': ultimo.color,
                    'temperatura': ultimo.temperatura,
                    'distancia': ultimo.distancia,
                    'nivel': ultimo.nivel,
                    'paciente': f"{ultimo.sesion.paciente.nombre} {ultimo.sesion.paciente.apellido}",
                }
                self.send(text_data=json.dumps(datos))
