"""
Actions to be used in consumers.py file.

"""

import os
import json
import socket
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.forms.models import model_to_dict

from .models import Arm, Session, UI, Log
from .ecs import ECSManager


if os.getenv("MODE") == "production" and os.getenv("FROM_DOCKER") == "1":
    ecsManager = ECSManager()


def register_arm(arm_id):
    """
    Add arm to DB is this is the first time checking in, otherwise update last_online timestamp.

    """

    new_arm = Arm(arm_id=arm_id, last_online=datetime.now())
    new_arm.save()


def get_cloud_ip():
    """
    In production mode, retrieve the IP address of the Cloud service and check if it's a valid IP. If not, return 0.
    In local mode, just return 'Local Mode'.

    """

    # Get SorterBot Cloud status from DB
    cloud_status = ecsManager.status() if os.getenv("MODE") == "production" else "Local Mode"

    # Check if status is a valid IP by trying to parse
    cloud_ip = 0
    try:
        socket.inet_aton(cloud_status)
        cloud_ip = cloud_status
    except socket.error:
        pass

    return cloud_ip


def push_arm_status(arm_id, cloud_connect_success):
    """
    Send arm status to frontend though Django channels.

    """

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("default", {
        "type": "push.arm.status",
        "arm_id": arm_id,
        "cloud_connect_success": cloud_connect_success
    })


def should_start_arm(arm_id):
    """
    Check in database if the current arm_id is in the list of arms to be started. If yes, remove it and return 1, otherwise return 0.

    """

    # Get current UI object and convert it to dict
    ui_objects = UI.objects.all()
    if len(ui_objects) > 0:
        current_UI = model_to_dict(ui_objects[0])
    else:
        # If row is empty, create one with default value
        UI(arms_to_start="[]").save()
        current_UI = model_to_dict(UI.objects.all()[0])

    try:
        # Remove arm id from list of arms to be started after command was sent back
        arms_to_start = json.loads(current_UI["arms_to_start"])
        arms_to_start.remove(arm_id)
        UI(arms_to_start=json.dumps(arms_to_start)).save()
        should_start = 1
    except ValueError:
        should_start = 0

    return should_start
