"""
Views and ViewSets to define REST endpoints.

"""

import os
import json
import socket
from datetime import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Arm, Session, UI, Log
from .serializers import ArmSerializer, SessionSerializer, UISerializer
from .ecs import ECSManager


if os.getenv("MODE") == "production" and os.getenv("FROM_DOCKER") == 1:
    ecsManager = ECSManager()


@login_required
@require_http_methods(["GET"])
def index(request):
    """
    Root endpoint to serve the frontend's HTML template.

    """

    try:
        with open(os.path.join(settings.BASE_DIR, 'templates', 'main.html')) as f:
            return HttpResponse(f.read())
    except FileNotFoundError:
        return HttpResponse(
            """
            This URL is only used when you have built the production
            version of the app. Visit http://localhost:3000/ instead, or
            run `yarn run build` to test the production version.
            """,
            status=501,
        )


# @csrf_exempt
# @api_view(["POST"])
# def get_cloud_ip(request):
#     arm_id = json.loads(request.body)["arm_id"]

#     # Add arm to DB is this is the first time checking in, otherwise update last_online timestamp
#     new_arm = Arm(arm_id=arm_id, last_online=datetime.now())
#     new_arm.save()

#     # Get SorterBot Cloud status from DB
#     cloud_status = ecsManager.status() if os.getenv("MODE") == "production" else "Local Mode"

#     # Check if status is a valid IP by trying to parse
#     status_res = False
#     try:
#         socket.inet_aton(cloud_status)
#         status_res = cloud_status
#     except socket.error:
#         pass

#     return Response({"cloud_ip": status_res}, status=status.HTTP_200_OK)


# @csrf_exempt
# @api_view(["POST"])
# def send_connection_status(request):
#     # Retrieve payload from request
#     arm_id = json.loads(request.body)["arm_id"]
#     cloud_connect_success = json.loads(request.body)["cloud_connect_success"]

#     # Send payload to frontend though channels
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)("default", {
#         "type": "push.arm.status",
#         "arm_id": arm_id,
#         "cloud_connect_success": cloud_connect_success
#     })

#     # Get current UI object and convert it to dict
#     ui_objects = UI.objects.all()
#     if len(ui_objects) > 0:
#         current_UI = model_to_dict(ui_objects[0])
#     else:
#         # If row is empty, create one with default value
#         UI(arms_to_start="[]").save()
#         current_UI = model_to_dict(UI.objects.all()[0])

#     # Remove arm id from list of arms to be started after command was sent back
#     arms_to_start = json.loads(current_UI["arms_to_start"])
#     try:
#         arms_to_start.remove(arm_id)
#     except ValueError:
#         pass
#     UI(arms_to_start=json.dumps(arms_to_start)).save()

#     # Send back command to start (or not) a new session
#     return Response({"should_start_session": arm_id in current_UI["arms_to_start"]}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def log(request):
    """
    Define an enpoint for the logs to be POSTed by Python logger's HTTP handlers.

    Parameters
    ----------
    request : JSON string
        Request containing the log entry.

    Returns
    -------
    response : HTTP Response
        Result of saving the log.
    """

    is_final_log = False
    new_log_args = {}

    args = json.loads(request.data["args"].replace("'", '"'))

    try:
        session_id = int(args["session_id"][1:])
        session = Session.objects.get(arm_id=args["arm_id"], id=session_id)
    except KeyError:
        # Don't save log if no session_id is provided
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Refresh session status if final log is received
    try:
        if args["session_finished"]:
            session.status = "Completed"
            session.save()
            return Response(status=status.HTTP_200_OK)
    except KeyError:
        pass

    # Add log to postgres if not last log of session
    for field in Log._meta.get_fields():
        # PK field 'id' does not exist in logger object, so skip it
        if field.name == "id":
            continue
        # Retrieve 'log_type' from args
        if field.name == "log_type":
            new_log_args[field.name] = args[field.name]
            continue
        # Retrieve 'bm_id' from args (if it exists)
        if field.name == "bm_id":
            try:
                new_log_args[field.name] = args[field.name]
            except KeyError:
                new_log_args[field.name] = 0
            continue
        # Field 'arm' expects an Arm object, so retrieve it based on 'arm_id' from args
        if field.name == "arm":
            new_log_args[field.name] = Arm.objects.get(arm_id=args["arm_id"])
            continue
        # Field 'session' expects a Session object, so retrieve it based on 'session_id' from args
        if field.name == "session":
            new_log_args[field.name] = Session.objects.get(id=session_id)
            continue
        new_log_args[field.name] = request.data[field.name]

    # Save new log entry to Postgres
    Log(**new_log_args).save()

    # Set enabled log types on Session to accurately enable/disable log type buttons on front-end
    current_logtypes = session.enabled_log_types or "[]"
    current_logtypes = json.loads(current_logtypes)
    new_logtypes = current_logtypes + [str(args["log_type"])]
    no_dupl_logtypes = list(set(new_logtypes))
    session.enabled_log_types = json.dumps(no_dupl_logtypes)

    session.save()

    # Refresh sessions on front-end if there is a new log type or session finished
    if not str(args["log_type"]) in current_logtypes or is_final_log:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)("default", {
            "type": "push.sessions.of.arm",
            "arm_id": args["arm_id"]
        })

    return Response(status=status.HTTP_200_OK)


class ArmViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage arms with REST requests.

    """

    queryset = Arm.objects.all()
    serializer_class = ArmSerializer

    def create(self, request):
        """
        Explicitly provide primary key (id) so the entry is updated, instead of a new being added if arm already exists in db.

        """

        new_arm = Arm(arm_id=request.data["arm_id"], last_online=request.data["last_online"])
        new_arm.save()
        return Response(request.data, status=status.HTTP_201_CREATED)


class SessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage sessions with REST requests.

    """

    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    def create(self, request):
        """
        Override create to insert appropriate entities to the database instead of their string representations.

        """

        try:
            # Convert timestamp to datetime
            request.data["session_started"] = datetime.fromtimestamp(request.data["session_started"])

            # Replace arm_id with Arm instance
            request.data["arm"] = Arm.objects.get(arm_id=request.data["arm"])

            # Save new session
            new_session = Session(**request.data)
            new_session.save()

            return Response(json.dumps({"new_session_id": f"S{new_session.id}"}), status=status.HTTP_200_OK)
        except Exception as e:
            print(e)


class UIViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage UI variables with REST requests.

    """

    queryset = UI.objects.all()
    serializer_class = UISerializer

    def create(self, request):
        UI(**request.data).save()

        # Get whole updated UI object and send it back with the response
        updated_ui = model_to_dict(UI.objects.all()[0])

        return Response(updated_ui, status=status.HTTP_200_OK)
