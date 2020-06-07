"""
Functions to retrieve status, start or stop ECS tasks.

"""

import os
import boto3
from time import sleep
import channels.layers
from asgiref.sync import async_to_sync


class ECSManager:
    """
    A class to organize functions related to the ECS cluster. On init, neccessary AWS clients are initiated, ECS cluster looked up by tag,
    then initial status pushed to frontend.

    """

    def __init__(self):
        # Define Clients
        session = boto3.Session(region_name=os.getenv("DEPLOY_REGION"))
        self.ecs_client = session.client('ecs')
        self.ec2_client = session.client('ec2')

        # Define waiters
        self.on_waiter = self.ecs_client.get_waiter('tasks_running')
        self.off_waiter = self.ecs_client.get_waiter('tasks_stopped')

        # Retrieve ECS Cluster by tag
        clusterArns = self.ecs_client.list_clusters()["clusterArns"]
        clusters = self.ecs_client.describe_clusters(clusters=clusterArns, include=["TAGS"])["clusters"]

        try:
            self.cluster = next(cluster for cluster in clusters if "SorterBotResource" in [tag["key"] for tag in cluster["tags"]])["clusterArn"]
        except StopIteration:
            raise Exception('No ECS Cluster was found with the following tag key "SorterBotResource"')

        # Retrieve Service of given Cluster by index (not by tag, because it needs the new ARN format enabled account wide, which would increase complexity)
        self.service = self.ecs_client.list_services(cluster=self.cluster)["serviceArns"][0]

        # Retrieve channel layer for real time messaging
        self.channel_layer = channels.layers.get_channel_layer()

        async_to_sync(self.channel_layer.group_send)("default", {
            "type": "push.cloud.status",
            "status": self.status()
        })

    def status(self):
        """
        Determines ECS task's status. 
        - If there are no tasks in the cluster, and desired count is 0, the status is 'off'.
        - If there are no tasks, but the desired count is not 0, status is 'startLoading'.
        - If there is at least 1 task, but the desired count is 0, status is 'stopLoading'.
        - If there is at least 1 task, and it's status is not RUNNING, the status is 'startLoading'.
        - If there is at least 1 task, and it's status is RUNNING, the status is it's public IP address.

        Returns
        -------
        status : str
            The status of the task according to the rules described above.

        """

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
        """
        Starts Cloud service by increasing desired_count to 1. After that, it waits until the task is running, then pushes a status update.

        """

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
        """
        Retrieves the public IP of the running task.

        Returns
        -------
        public_ip : str
            Public IP of the running task.

        """

        # Retrieve Network Interface ID from given Task
        tasksDescriptions = self.ecs_client.describe_tasks(cluster=self.cluster, tasks=taskArns)["tasks"]
        network_interface_id = next(detail["value"] for detail in tasksDescriptions[0]["attachments"][0]["details"] if detail["name"] == "networkInterfaceId")
        print(f"Network Interface ID retrieved: {network_interface_id}")

        # Retrieve Public IP from given Network Interface ID
        network_interfaces = self.ec2_client.describe_network_interfaces(NetworkInterfaceIds=[network_interface_id])["NetworkInterfaces"]
        public_ip = network_interfaces[0]["Association"]["PublicIp"]

        return public_ip

    def stop(self):
        """
        Stops Cloud service by decreasing desired_count to 0. After that, it waits until the task is stopped, then pushes a status update.

        """

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
