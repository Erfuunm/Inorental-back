import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inorental.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        # Just for now, we will add websocket later
        # "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter([]))),
    }
)
