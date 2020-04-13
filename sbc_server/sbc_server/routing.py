from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import sorterbot_control_panel.routing


application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            sorterbot_control_panel.routing.websocket_urlpatterns
        )
    ),
})
