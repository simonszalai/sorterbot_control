import json
import socket
from datetime import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Arm, Session, UI
from .serializers import ArmSerializer, SessionSerializer, UISerializer
from .ecs import ECSManager


@require_http_methods(["GET"])
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@csrf_exempt
@api_view(["POST"])
def get_cloud_ip(request):
    arm_id = json.loads(request.body)["arm_id"]

    # Add arm to DB is this is the first time checking in, otherwise update last_online timestamp
    new_arm = Arm(arm_id=arm_id, last_online=datetime.now())
    new_arm.save()

    # Get SorterBot Cloud status from DB
    cloud_status = ECSManager().status()

    # Check if status is a valid IP by trying to parse
    status_res = False
    try:
        socket.inet_aton(cloud_status)
        status_res = cloud_status
    except socket.error:
        pass

    return Response({"cloud_ip": status_res}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def send_connection_status(request):
    arm_id = json.loads(request.body)["arm_id"]
    cloud_connect_success = json.loads(request.body)["cloud_connect_success"]
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("default", {
        "type": "arm.conn.status",
        "arm_id": arm_id,
        "cloud_connect_success": cloud_connect_success
    })
    return Response(status=status.HTTP_200_OK)


class ArmViewSet(viewsets.ModelViewSet):
    queryset = Arm.objects.all()
    serializer_class = ArmSerializer

    def create(self, request):
        """
        Explicitly provide primary key (id) so the entry is updated, instead of a new being added

        """

        new_arm = Arm(arm_id=request.data["arm_id"], last_online=request.data["last_online"])
        new_arm.save()
        return Response(request.data, status=status.HTTP_201_CREATED)


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class UIViewSet(viewsets.ModelViewSet):
    queryset = UI.objects.all()
    serializer_class = UISerializer

    def create(self, request):
        """
        Explicitly provide primary key (id) so the entry is updated, instead of a new being added

        """
        current_UI = UI.objects.all()[0]
        new_ui = UI(
            id=request.data["id"],
            cloud_status=request.data["cloud_status"] or current_UI.cloud_status,
            start_session=request.data["start_session"] or current_UI.start_session
        )
        new_ui.save()
        return Response(request.data, status=status.HTTP_201_CREATED)
