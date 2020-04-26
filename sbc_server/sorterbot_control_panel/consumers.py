import json
from channels.generic.websocket import WebsocketConsumer
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict

from .models import UI
from .ecs import ECSManager
from .database import DB
from .s3 import S3


class SBCConsumer(WebsocketConsumer):
    groups = ["default"]

    def connect(self):
        print("Connecting")
        self.db = DB()
        self.s3 = S3()
        self.ecsManager = ECSManager()
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
        content = {}

        if command_in == "fetch_arms":
            content = {
                "command": "arms",
                "arms": self.db.get_arms()
            }
            self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))  # DjangoJSONEncoder to serialize Datetime properly

        elif command_in == "fetch_sessions_of_arm":
            content = {
                "command": "sessions_of_arm",
                "sessionsOfArm": self.db.get_sessions_of_arm(data["arm_id"])
            }
            self.send(text_data=json.dumps(content))

        elif command_in == "fetch_logs":
            content = {
                "command": "logs",
                "logs": self.db.get_logs(arm_id=data["arm_id"], session_id=data["sess_id"], log_type=data["log_type"])
            }
            self.send(text_data=json.dumps(content))

        elif command_in == "fetch_stitch":
            session = self.db.get_session_by_id(data["sess_id"])
            stitch_name = f'{data["log_type"].lower()}_stitch.jpg'
            content = {
                "command": "stitch",
                "stitch_url": self.s3.get_signed_url(s3_path=f'{data["arm_id"]}/{session.session_id}/{stitch_name}')
            }
            self.send(text_data=json.dumps(content))

        elif command_in == "fetch_cloud_status":
            content = {
                "command": "cloud_status",
                "cloudStatus": self.ecsManager.status()
            }
            self.send(text_data=json.dumps(content))

        elif command_in == "start_cloud":
            self.ecsManager.start()

        elif command_in == "stop_cloud":
            self.ecsManager.stop()

        elif command_in == "start_session":
            sessions_to_start = json.loads(model_to_dict(UI.objects.all()[0])["arms_to_start"])
            sessions_to_start.append(data["arm_id"])
            UI(arms_to_start=json.dumps(sessions_to_start)).save()

        elif command_in == "set_open_logs":
            UI(open_logs=data["open_logs"]).save()

    def push_arms(self, event):
        content = {
            "command": "arms",
            "arms": self.db.get_arms()
        }
        self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))  # DjangoJSONEncoder to serialize Datetime properly

    def push_sessions_of_arm(self, event):
        content = {
            "command": "sessions_of_arm",
            "sessionsOfArm": self.db.get_sessions_of_arm(arm_id=event["arm_id"])
        }
        self.send(text_data=json.dumps(content))

    def push_logs(self, event):
        content = {
            "command": "logs",
            "logs": self.db.get_logs(arm_id=event["arm_id"], session_id=event["sess_id"], log_type=event["log_type"])
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

    # def fetch_arms(self):
    #     arms = Arm.objects.all().order_by("arm_id")
    #     return [model_to_dict(arm) for arm in arms]

    # def fetch_sessions_of_arm(self, arm_id):
    #     sessions_of_arm = Session.objects.filter(arm=arm_id).order_by("-session_id")
    #     return [model_to_dict(session) for session in sessions_of_arm]



    # def fetch_logs(self, data):
    #     logs = Log.objects.filter(arm=data["arm_id"], session=data["sess_id"], log_type=data["log_type"]).order_by("created")
    #     return [model_to_dict(log) for log in logs]
