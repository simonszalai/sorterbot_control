import os
import boto3
from time import sleep
import channels.layers
from asgiref.sync import async_to_sync


class ECSManager:
    def __init__(self):
        # Define Clients
        session = boto3.Session()
        self.ecs_client = session.client('ecs')
        self.ec2_client = session.client('ec2')

        # Define waiters
        self.on_waiter = self.ecs_client.get_waiter('tasks_running')
        self.off_waiter = self.ecs_client.get_waiter('tasks_stopped')

        # Retrieve ECS Cluster by tag
        clusterArns = self.ecs_client.list_clusters()["clusterArns"]
        clusters = self.ecs_client.describe_clusters(clusters=clusterArns, include=["TAGS"])["clusters"]

        try:
            self.cluster = next(cluster for cluster in clusters if {"key": "SBID", "value": "SBCluster"} in cluster["tags"])["clusterArn"]
        except StopIteration:
            raise Exception('No ECS Cluster was found with the following tag: {"key": "SBID", "value": "SBCluster"}')

        # Retrieve Service of given Cluster by index (not by tag, because it needs the new ARN format enabled account wide, which would increase complexity)
        self.service = self.ecs_client.list_services(cluster=self.cluster)["serviceArns"][0]

        # Retrieve channel layer for real time messaging
        self.channel_layer = channels.layers.get_channel_layer()

        async_to_sync(self.channel_layer.group_send)("default", {
            "type": "push.cloud.status",
            "status": self.status()
        })

    def status(self):
        taskArns = self.ecs_client.list_tasks(cluster=self.cluster)["taskArns"]
        desired_count = self.ecs_client.describe_services(cluster=self.cluster, services=[self.service])["services"][0]["desiredCount"]

        if len(taskArns) == 0:
            if desired_count == 0:
                return "off"
            else:
                return "startLoading"
        else:
            tasksDescriptions = self.ecs_client.describe_tasks(cluster=self.cluster, tasks=taskArns)["tasks"]
            if desired_count == 0:
                return "stopLoading"
            else:
                if tasksDescriptions[0]["lastStatus"] == "RUNNING":
                    return self.get_public_ip(taskArns)
                else:
                    return "startLoading"

    def start(self):
        print("Turning on...")

        # Update desired task count
        desired_count = 0
        while desired_count == 0:
            print("Updating desired count...")
            self.ecs_client.update_service(cluster=self.cluster, service=self.service, desiredCount=1)
            desired_count = self.ecs_client.describe_services(cluster=self.cluster, services=[self.service])["services"][0]["desiredCount"]
            sleep(1)
        print("Service desired task count updated!")

        tasks_count = 0
        waited = 0
        taskArns = []
        while tasks_count == 0:
            # Retrieve Tasks in given Cluster
            taskArns = self.ecs_client.list_tasks(cluster=self.cluster)["taskArns"]
            tasks_count = len(taskArns)
            sleep(1)
            waited += 1

        print(f"Task added after {waited}s.")

        # Wait for Task to start
        self.on_waiter.wait(cluster=self.cluster, tasks=[taskArns[0]])
        print("Task started.")
        public_ip = self.get_public_ip(taskArns)

        async_to_sync(self.channel_layer.group_send)("default", {
            "type": "push.cloud.status",
            "status": public_ip
        })

    def get_public_ip(self, taskArns):
        # Retrieve Network Interface ID from given Task
        tasksDescriptions = self.ecs_client.describe_tasks(cluster=self.cluster, tasks=taskArns)["tasks"]
        network_interface_id = next(detail["value"] for detail in tasksDescriptions[0]["attachments"][0]["details"] if detail["name"] == "networkInterfaceId")
        print(f"Network Interface ID retrieved: {network_interface_id}")

        # Retrieve Public IP from given Network Interface ID
        network_interfaces = self.ec2_client.describe_network_interfaces(NetworkInterfaceIds=[network_interface_id])["NetworkInterfaces"]
        public_ip = network_interfaces[0]["Association"]["PublicIp"]

        return public_ip

    def stop(self):
        print("Turning off...")

        desired_count = 1
        while desired_count == 1:
            print("Updating desired count...")
            self.ecs_client.update_service(cluster=self.cluster, service=self.service, desiredCount=0)
            desired_count = self.ecs_client.describe_services(cluster=self.cluster, services=[self.service])["services"][0]["desiredCount"]
            sleep(1)
        print("Service desired task count updated!")

        async_to_sync(self.channel_layer.group_send)("default", {
            "type": "push.cloud.status",
            "status": "stopLoading"
        })

        taskArns = self.ecs_client.list_tasks(cluster=self.cluster)["taskArns"]
        self.off_waiter.wait(cluster=self.cluster, tasks=[taskArns[0]])
        print("Task stopped.")

        async_to_sync(self.channel_layer.group_send)("default", {
            "type": "push.cloud.status",
            "status": "off"
        })
