import json
from channels.generic.websocket import WebsocketConsumer
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict

from .models import Arm, Session, UI, Log
from .ecs import ECSManager


class SBCConsumer(WebsocketConsumer):
    groups = ["default"]

    def connect(self):
        print("Connecting")
        self.ecsManager = ECSManager()
        self.channel_layer.group_add("default", self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        if not hasattr(self, "groups"):
            return
        for group in self.groups:
            self.channel_layer.group_discard(group, self.channel_name)

    def receive(self, text_data):
        data = json.loads(text_data)
        command = data["command"]
        print(command)
        content = {"command": command}

        if command == "fetch_arms":
            arms_list = self.fetch_arms()
            content["arms"] = arms_list
            self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))  # DjangoJSONEncoder to serialize Datetime properly

        elif command == "fetch_sessions_of_arm":
            sessions = self.fetch_sessions_of_arm(data["armId"])
            content["sessions"] = sessions
            self.send(text_data=json.dumps(content))

        elif command == "fetch_logs":
            logs = self.fetch_logs(data)
            content["logs"] = logs
            self.send(text_data=json.dumps(content))

        elif command == "set_open_logs":
            UI(open_logs=data["open_logs"]).save()

        elif command == "cloud_status":
            content["status"] = self.ecsManager.status()
            self.send(text_data=json.dumps(content))

        elif command == "cloud_start":
            public_ip = self.ecsManager.start()
            content["publicIp"] = public_ip
            self.send(text_data=json.dumps(content))

        elif command == "cloud_stop":
            self.ecsManager.stop()
            self.send(text_data=json.dumps(content))

        elif command == "start_session":
            arm_id = data["armId"]
            UI(start_session=True).save()

    def arm_added(self, event):
        content = {"command": "fetch_arms"}
        arms_list = self.fetch_arms()
        content["arms"] = arms_list
        self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))  # DjangoJSONEncoder to serialize Datetime properly

    def push_logs(self, event):
        content = {"command": "fetch_logs"}
        logs = Log.objects.filter(arm=event["arm_id"], session=event["sess_id"], log_type=event["log_type"]).order_by("created")
        print(logs)
        content["logs"] = [model_to_dict(log) for log in logs]
        self.send(text_data=json.dumps(content))

    def status_changed(self, event):
        self.send(text_data=json.dumps({
            "command": "cloud_status",
            "status": event["status"]
        }))

    def arm_conn_status(self, event):
        self.send(text_data=json.dumps({
            "command": "arm_conn_status",
            "armId": event["arm_id"],
            "cloudConnectSuccess": event["cloud_connect_success"]
        }))

    def fetch_arms(self):
        arms = Arm.objects.all()
        return [model_to_dict(arm) for arm in arms]

    def fetch_sessions_of_arm(self, arm_id):
        sessions_of_arm = Session.objects.filter(arm=arm_id).order_by("-session_id")
        return [model_to_dict(session) for session in sessions_of_arm]

    def push_sessions_of_arm(self, event):
        self.send(text_data=json.dumps({
            "command": "fetch_sessions_of_arm",
            "sessions": self.fetch_sessions_of_arm(arm_id=event["arm_id"]),
        }))

    def fetch_logs(self, data):
        logs = Log.objects.filter(arm=data["arm_id"], session=data["sess_id"], log_type=data["log_type"]).order_by("created")
        return [model_to_dict(log) for log in logs]
