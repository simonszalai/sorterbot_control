import json
from channels.generic.websocket import WebsocketConsumer
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync

from sorterbot_control_panel import models
from .models import Arm, Session
from .ecs import ECSManager


class SBCConsumer(WebsocketConsumer):
    groups = ["default"]

    def connect(self):
        print("Connecting")
        self.ecsManager = ECSManager()
        self.channel_layer.group_add('default', self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        self.channel_layer.group_discard('default', self.channel_name)

    def receive(self, text_data):
        data = json.loads(text_data)
        command = data['command']
        content = {"command": command}

        if command == 'fetch_arms':
            arms_list = self.fetch_arms()
            content["arms"] = arms_list
            self.send(text_data=json.dumps(content))

        elif command == 'cloud_status':
            content["status"] = self.ecsManager.status()
            self.send(text_data=json.dumps(content))

        elif command == 'cloud_start':
            public_ip = self.ecsManager.start()
            content["publicIp"] = public_ip
            self.send(text_data=json.dumps(content))

        elif command == 'cloud_stop':
            self.ecsManager.stop()
            self.send(text_data=json.dumps(content))

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
        return arms_list
