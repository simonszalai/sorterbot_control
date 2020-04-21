import json
import socket
from datetime import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Arm, Session, UI, Log
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
    # Retrieve payload from request
    arm_id = json.loads(request.body)["arm_id"]
    cloud_connect_success = json.loads(request.body)["cloud_connect_success"]

    # Send payload to frontend though channels
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("default", {
        "type": "arm.conn.status",
        "arm_id": arm_id,
        "cloud_connect_success": cloud_connect_success
    })

    # Get current UI object and convert it to dict
    ui_objects = UI.objects.all()
    if len(ui_objects) > 0:
        current_UI = model_to_dict(UI.objects.all()[0])
    else:
        UI(start_session=False).save()

    # Reset flag after command was sent
    UI(start_session=False).save()

    # Send back command to start (or not) a new session
    return Response({"should_start_session": current_UI["start_session"]}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def log(request):
    new_log_args = {}
    for field in Log._meta.get_fields():
        args = json.loads(request.data["args"].replace("'", '"'))
        # PK field 'id' does not exist in logger object, so skip it
        if field.name == "id":
            continue
        # Retrieve 'log_type' from args
        if field.name == "log_type":
            new_log_args[field.name] = args[field.name]
            continue
        # Field 'arm' expects an Arm object, so retrieve it based on 'arm_id' from args
        if field.name == "arm":
            new_log_args[field.name] = Arm.objects.get(arm_id=args["arm_id"])
            continue
        # Field 'session' expects a Session object, so retrieve it based on 'session_id' from args
        if field.name == "session":
            new_log_args[field.name] = Session.objects.get(session_id=args["session_id"])
            continue
        new_log_args[field.name] = request.data[field.name]

    # Save new log entry to Postgres
    Log(**new_log_args).save()

    # Set enabled log types on Session to accurately enable/disable log type buttons on front-end
    session = Session.objects.get(arm_id=args["arm_id"], session_id=args["session_id"])
    current_logtypes = session.enabled_log_types.split(",")
    new_logtypes = current_logtypes + [str(args["log_type"])]
    no_dupl_logtypes = list(set(new_logtypes))
    session.enabled_log_types = ",".join(no_dupl_logtypes)
    session.save()

    # Refresh sessions on front-end if there is a new log type
    if not str(args["log_type"]) in current_logtypes:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)("default", {
            "type": "push.sessions.of.arm",
            "arm_id": args["arm_id"]
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
        UI(**request.data).save()

        # Get whole updated UI object and send it back with the response
        updated_ui = model_to_dict(UI.objects.all()[0])

        return Response(updated_ui, status=status.HTTP_200_OK)
