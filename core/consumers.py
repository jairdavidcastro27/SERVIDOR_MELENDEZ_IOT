import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DatosRealtimeConsumer(AsyncWebsocketConsumer):
    # Define un nombre de grupo para la comunicación
    group_name = 'telemetria_realtime'

    async def connect(self):
        # Cuando un cliente se conecta...
        # Unirse al grupo de telemetría
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Cuando un cliente se desconecta...
        # Salir del grupo
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Este método se llama automáticamente cuando se recibe un mensaje del grupo
    # con {'type': 'telemetria.update'}
    async def telemetria_update(self, event):
        datos = event['datos']

        # Enviar los datos al cliente WebSocket
        await self.send(text_data=json.dumps(datos))
