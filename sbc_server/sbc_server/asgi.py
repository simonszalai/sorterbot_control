"""
ASGI config for sbc_server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/

"""

import os

# from django.core.asgi import get_asgi_application
from channels.asgi import get_channel_layer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sbc_server.settings')

# application = get_asgi_application()
channel_layer = get_channel_layer()
