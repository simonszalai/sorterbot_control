import json
from channels.generic.websocket import WebsocketConsumer
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync

from sorterbot_control_panel import models
from .models import Arm, Session


class SBCConsumer(WebsocketConsumer):
    groups = ["default"]

    def connect(self):
        print("Connecting")
        self.channel_layer.group_add('default', self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        self.channel_layer.group_discard('default', self.channel_name)

    def receive(self, text_data):
        data = json.loads(text_data)
        command = data['command']

        if command == 'fetch_arms':
            self.fetch_arms()

    def arm_added(self, event):
        print('arm_added')
        self.fetch_arms()

    def fetch_arms(self):
        arms = models.Arm.objects.all()
        arms_list = []
        for arm in arms:
            arms_list.append({
                "arm_id": arm.arm_id,
                "arm_address": arm.arm_address
            })

        content = {
            "command": "fetch_arms",
            "arms": arms_list
        }
        print(arms_list)
        self.send(text_data=json.dumps(content))
