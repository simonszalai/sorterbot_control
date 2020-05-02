import boto3
from time import sleep
import channels.layers
from asgiref.sync import async_to_sync


class ECSManager:
    def __init__(self):
        # Define Clients
        self.ecs_client = boto3.client('ecs')
        self.ec2_client = boto3.client('ec2')

        # Define waiters
        self.on_waiter = self.ecs_client.get_waiter('tasks_running')
        self.off_waiter = self.ecs_client.get_waiter('tasks_stopped')

        # Retrieve Cluster ARNs
        self.cluster = self.ecs_client.list_clusters()["clusterArns"][0]

        # Retrieve Services of given Cluster
        self.service = self.ecs_client.list_services(cluster=self.cluster)["serviceArns"][0]

        # Retrieve channel layer for real time messaging
        self.channel_layer = channels.layers.get_channel_layer()

        # # TODO: if server restarts after a task start button was clicked but before the task was added, this fails
        # taskArns = self.ecs_client.list_tasks(cluster=self.cluster)["taskArns"]
        # if len(taskArns) == 0:
        #     pass
        #     # UI(cloud_status="off").save()
        # else:
        #     tasksDescriptions = self.ecs_client.describe_tasks(cluster=self.cluster, tasks=taskArns)["tasks"]
        #     if tasksDescriptions[0]["attachments"][0]["status"] == "RUNNING":
        #         public_ip = self.get_public_ip(taskArns)
        #         UI(cloud_status=public_ip).save()
        #     else:
        #         UI(cloud_status="startLoading").save()

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
                if tasksDescriptions[0]["attachments"][0]["status"] == "RUNNING":
                    return self.get_public_ip(taskArns)
                else:
                    return "startLoading"

    def start(self):
        print("Turning on...")
        # UI(cloud_status="startLoading").save()

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
        # UI(cloud_status=public_ip).save()

        async_to_sync(self.channel_layer.group_send)("default", {
            "type": "push.cloud.status",
            "status": public_ip
        })

    def get_public_ip(self, taskArns):
        # Retrieve Network Interface ID from given Task
        tasksDescriptions = self.ecs_client.describe_tasks(cluster=self.cluster, tasks=taskArns)["tasks"]
        network_interface_id = next(detail["value"] for detail in tasksDescriptions[0]["attachments"][0]["details"] if detail["name"] == "networkInterfaceId")
        print("Network Interface ID retrieved!")

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

        # UI(cloud_status="stopLoading").save()
        async_to_sync(self.channel_layer.group_send)("default", {
            "type": "push.cloud.status",
            "status": "stopLoading"
        })

        taskArns = self.ecs_client.list_tasks(cluster=self.cluster)["taskArns"]
        self.off_waiter.wait(cluster=self.cluster, tasks=[taskArns[0]])
        print("Task stopped.")
        # UI(cloud_status="off").save()

        async_to_sync(self.channel_layer.group_send)("default", {
            "type": "push.cloud.status",
            "status": "off"
        })
