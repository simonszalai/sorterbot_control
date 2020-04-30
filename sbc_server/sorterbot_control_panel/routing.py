from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'websocket/$', consumers.SBCConsumer),
    re_path(r'rpi/$', consumers.RPiConsumer),
]
