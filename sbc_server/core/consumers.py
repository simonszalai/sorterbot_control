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
s3 = S3()
ecsManager = ECSManager()


class SBCConsumer(WebsocketConsumer):
    groups = ["default"]

    def connect(self):
        print("Connecting default")
        self.channel_layer.group_add("default", self.channel_name)
        self.accept()

        print(self.scope["user"])

    def disconnect(self, close_code):
        if not hasattr(self, "groups"):
            return
        for group in self.groups:
            self.channel_layer.group_discard(group, self.channel_name)

    def receive(self, text_data):
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
            self.send(text_data=json.dumps(content))

        elif command_in == "fetch_logs":
            content = {
                "command": "logs",
                "logs": db.get_logs(arm_id=data["arm_id"], session_id=data["sess_id"], log_type=data["log_type"])
            }
            self.send(text_data=json.dumps(content))

        elif command_in == "fetch_stitch":
            session = db.get_session_by_id(data["sess_id"])
            stitch_name = f'{data["log_type"].lower()}_stitch.jpg'
            content = {
                "command": "stitch",
                "stitch_url": s3.get_signed_url(s3_path=f'{data["arm_id"]}/{session.session_id}/{stitch_name}')
            }
            self.send(text_data=json.dumps(content))

        elif command_in == "fetch_cloud_status":
            content = {
                "command": "cloud_status",
                "cloudStatus": ecsManager.status()
            }
            self.send(text_data=json.dumps(content))

        elif command_in == "start_cloud":
            ecsManager.start()

        elif command_in == "stop_cloud":
            ecsManager.stop()

        elif command_in == "start_session":
            sessions_to_start = json.loads(model_to_dict(UI.objects.all()[0])["arms_to_start"])
            sessions_to_start.append(data["arm_id"])
            UI(arms_to_start=json.dumps(sessions_to_start)).save()

        elif command_in == "set_open_logs":
            UI(open_logs=data["open_logs"]).save()

        elif command_in == "logout":
            print("logout")
            async_to_sync(logout)(self.scope)
            return redirect("/")

    def push_arms(self, event):
        content = {
            "command": "arms",
            "arms": db.get_arms()
        }
        self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))  # DjangoJSONEncoder to serialize Datetime properly

    def push_sessions_of_arm(self, event):
        content = {
            "command": "sessions_of_arm",
            "armId": event["arm_id"],
            "sessionsOfArm": db.get_sessions_of_arm(arm_id=event["arm_id"])
        }
        self.send(text_data=json.dumps(content))

    def push_logs(self, event):
        content = {
            "command": "logs",
            "logs": db.get_logs(arm_id=event["arm_id"], session_id=event["sess_id"], log_type=event["log_type"])
        }
        self.send(text_data=json.dumps(content))

    def push_cloud_status(self, event):
        content = {
            "command": "cloud_status",
            "cloud_status": event["status"]
        }
        self.send(text_data=json.dumps(content))

    def push_arm_status(self, event):
        content = {
            "command": "arm_status",
            "armId": event["arm_id"],
            "cloudConnectSuccess": event["cloud_connect_success"]
        }
        self.send(text_data=json.dumps(content))


class RPiConsumer(WebsocketConsumer):
    groups = ["rpi"]

    def connect(self):
        print("Connecting RPi")
        self.channel_layer.group_add("default", self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        if not hasattr(self, "groups"):
            return
        for group in self.groups:
            self.channel_layer.group_discard(group, self.channel_name)

    def receive(self, text_data):
        data = json.loads(text_data)
        command_in = data["command"]

        if command_in == "get_cloud_ip":
            cloud_ip = get_cloud_ip()
            cloud_ip = "192.168.178.19"
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