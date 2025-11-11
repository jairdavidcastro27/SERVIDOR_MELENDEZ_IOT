import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AllowedHostsOriginValidator
import core.routing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lentes_project.settings')

# La aplicación ASGI principal
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # AllowedHostsOriginValidator envuelve nuestro router para proteger contra ataques CSRF
    # a través de WebSockets, verificando el origen contra ALLOWED_HOSTS.
    "websocket": AllowedHostsOriginValidator(
        URLRouter(
            core.routing.websocket_urlpatterns
        )
    ),
})