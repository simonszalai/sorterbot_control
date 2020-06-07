"""
Define messages and message handlers for WebSockets communication between Django backend - React frontend as well as
Django backend - Raspberry Pis.

"""

import os
import json
from channels.generic.websocket import WebsocketConsumer
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from channels.auth import logout
from django.shortcuts import redirect
from asgiref.sync import async_to_sync

from .commands import get_cloud_ip, register_arm, push_arm_status, should_start_arm
from .models import UI
from .ecs import ECSManager
from .database import DB
from .s3 import S3


db = DB()

if os.getenv("MODE") == "production" and os.getenv("FROM_DOCKER") == "1":
    ecsManager = ECSManager()

if os.getenv("MODE") != "local":
    s3 = S3()


class SBCConsumer(WebsocketConsumer):
    """
    Define WebsocketConsumer for communication between Django backend and React frontend.

    """

    groups = ["default"]

    def connect(self):
        """
        Connect WebSocket client to group default.

        """

        self.channel_layer.group_add("default", self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        """
        Remove client from all of its groups (disconnect), and print reason.

        Parameters
        ----------
        close_code : int
            Reason code to disconnect the client.

        """

        if not hasattr(self, "groups"):
            return
        for group in self.groups:
            self.channel_layer.group_discard(group, self.channel_name)
        print(f"Frontend WebSockets client disconnecting, reason: {close_code}")

    def receive(self, text_data):
        """
        Define handlers for receiving messages through WebSockets. All the actions below are executed as a response to a request from the frontend.

        Commands:
        fetch_arms: Retrieve arms from database and send them back.
        fetch_sessions_of_arm: Retrieve session of the specified arm from database and send them back.
        fetch_logs: Retrieve session of the specified arm, session and logtype from database and send them back.
        fetch_stitch: Get signed URL from S3 of the stiched image, and send it back.
        fetch_cloud_status: Get cloud status from ECSManager, and send it back.
        start_cloud: Set the desired_count of tasks in the ECS Cluster to 1.
        stop_cloud: Set the desired_count of tasks in the ECS Cluster to 0.
        start_session: Add the current arm's ID to to list of arms to be started in the database. On next check-in, the arm will start.
        set_open_logs: Sets on the backend, which logs are currently open on the frontend, so only those will be pushed.
        logout: Logs out the current Django user.

        Parameters
        ----------
        text_data : str
            JSON containing command type and payload.

        """

        data = json.loads(text_data)
        command_in = data["command"]

        if command_in == "fetch_arms":
            content = {
                "command": "arms",
                "arms": db.get_arms()
            }
            self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))  # DjangoJSONEncoder to serialize Datetime properly

        elif command_in == "fetch_sessions_of_arm":
            content = {
                "command": "sessions_of_arm",
                "armId": data["arm_id"],
                "sessionsOfArm": db.get_sessions_of_arm(data["arm_id"])
            }
            self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))

        elif command_in == "fetch_logs":
            content = {
                "command": "logs",
                "logs": db.get_logs(arm_id=data["arm_id"], session_id=data["session_id"], log_type=data["log_type"])
            }
            self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))

        elif command_in == "fetch_stitch":
            session = db.get_session_by_id(data["session_id"])
            stitch_name = f'{"original" if data["log_type"].lower() == "before" else data["log_type"].lower()}_stitch.jpg'
            content = {
                "command": "stitch",
                "stitch_url": s3.get_signed_url(s3_path=f'{data["arm_id"]}/S{session.id}/{stitch_name}') if os.getenv("MODE") != "local" else ""
            }
            self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))

        elif command_in == "fetch_cloud_status":
            content = {
                "command": "cloud_status",
                "cloudStatus": ecsManager.status() if os.getenv("MODE") == "production" else "Local Mode"
            }
            self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))

        elif command_in == "start_cloud":
            if os.getenv("MODE") == "production":
                ecsManager.start()

        elif command_in == "stop_cloud":
            if os.getenv("MODE") == "production":
                ecsManager.stop()

        elif command_in == "start_session":
            sessions_to_start = json.loads(model_to_dict(UI.objects.all()[0])["arms_to_start"])
            sessions_to_start.append(data["arm_id"])
            UI(arms_to_start=json.dumps(sessions_to_start)).save()

        elif command_in == "set_open_logs":
            UI(open_logs=data["open_logs"]).save()

        elif command_in == "logout":
            async_to_sync(logout)(self.scope)
            return redirect("/")

    def push_arms(self, event):
        """
        Retrieve list of arms from database and push it to frontend.

        """

        content = {
            "command": "arms",
            "arms": db.get_arms()
        }
        self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))

    def push_sessions_of_arm(self, event):
        """
        Retrieve list of sessions of given arm from database and push it to frontend.

        Parameters
        ----------
        event : dict
            Dictionary containing the arm_id.

        """

        content = {
            "command": "sessions_of_arm",
            "armId": event["arm_id"],
            "sessionsOfArm": db.get_sessions_of_arm(arm_id=event["arm_id"])
        }
        self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))

    def push_logs(self, event):
        """
        Pushes updated logs to the frontend as they arrive. Only gets called for the currently open logs.

        Parameters
        ----------
        event : dict
            Dictionary containing the arm_id, session_id, and log_type.

        """

        content = {
            "command": "logs",
            "logs": db.get_logs(arm_id=event["arm_id"], session_id=event["session_id"], log_type=event["log_type"])
        }
        self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))

    def push_cloud_status(self, event):
        """
        Pushes Cloud service status changes during init, startup or shutdown.

        Parameters
        ----------
        event : dict
            Dictionary containing the cloud service's status.

        """

        content = {
            "command": "cloud_status",
            "cloud_status": event["status"]
        }
        self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))

    def push_arm_status(self, event):
        """
        Pushes arm status (connected or not to the Cloud service) to frontend when an arm checks in.

        Parameters
        ----------
        event : dict
            Dictionary containing the arm_id, and cloud_connect_success.

        """

        content = {
            "command": "arm_status",
            "armId": event["arm_id"],
            "cloudConnectSuccess": event["cloud_connect_success"]
        }
        self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))


class RPiConsumer(WebsocketConsumer):
    """
    Define WebsocketConsumer for communication between Django backend and a Raspberry Pi.

    """

    groups = ["rpi"]

    def connect(self):
        """
        Connect WebSocket client to group default.

        """

        self.channel_layer.group_add("default", self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        """
        Remove client from all of its groups (disconnect), and print reason.

        Parameters
        ----------
        close_code : int
            Reason code to disconnect the client.

        """

        if not hasattr(self, "groups"):
            return
        for group in self.groups:
            self.channel_layer.group_discard(group, self.channel_name)
        print(f"RPi WebSockets client disconnecting, reason: {close_code}")

    def receive(self, text_data):
        """
        Define handlers for receiving messages through WebSockets. All the actions below are executed as a response to a request from the frontend.

        Commands:
        get_cloud_ip: Retrieve Cloud service's IP address and send it back to the Raspberry Pi.
        send_conn_status: Handle the check-in from an arm. Push status to frontend, check is a session should be started and send back a response.

        Parameters
        ----------
        text_data : str
            JSON containing command type and payload.

        """

        data = json.loads(text_data)
        command_in = data["command"]

        if command_in == "get_cloud_ip":
            cloud_ip = get_cloud_ip()
            self.send(text_data=json.dumps(cloud_ip))

        elif command_in == "send_conn_status":
            arm_id = data["arm_id"]
            conn_status = data["cloud_conn_status"]

            # Register arm in case this is the first check-in
            register_arm(data["arm_id"])

            # Push arm connection status to UI to set the color of the status LED
            push_arm_status(arm_id, conn_status)

            # Only check if session should be started if arm is ready to execute
            if conn_status:
                should_start = should_start_arm(data["arm_id"])
            else:
                should_start = 0
            self.send(text_data=json.dumps(should_start))
