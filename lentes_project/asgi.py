import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import OriginValidator
import core.routing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lentes_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": OriginValidator(
        URLRouter(
            core.routing.websocket_urlpatterns
        ),
        [
            "https://servidormelendeziot-production.up.railway.app",
            "http://127.0.0.1:8000",
            "http://localhost:8000",
        ]
    ),
})
