import json
from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from django.core.serializers.json import DjangoJSONEncoder

from sorterbot_control_panel import models
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
        raise StopConsumer()

    def receive(self, text_data):
        data = json.loads(text_data)
        command = data["command"]
        content = {"command": command}

        if command == "fetch_arms":
            arms_list = self.fetch_arms()
            content["arms"] = arms_list
            self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))  # DjangoJSONEncoder to serialize Datetime properly

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
            print(arm_id)

    def arm_added(self, event):
        content = {"command": "fetch_arms"}
        arms_list = self.fetch_arms()
        content["arms"] = arms_list
        self.send(text_data=json.dumps(content, cls=DjangoJSONEncoder))  # DjangoJSONEncoder to serialize Datetime properly

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
        arms = models.Arm.objects.all()
        arms_list = []
        for arm in arms:
            arms_list.append({
                "arm_id": arm.arm_id,
                "last_online": arm.last_online
            })
        return arms_list
