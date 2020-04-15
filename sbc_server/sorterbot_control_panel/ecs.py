import boto3
from time import sleep
from .models import UI


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

    def status(self):
        all_status = UI.objects.all()
        if len(all_status) > 0:
            return all_status[0].cloud_status
        else:
            taskArns = self.ecs_client.list_tasks(cluster=self.cluster)["taskArns"]
            if len(taskArns) > 0:
                return self.get_public_ip(taskArns)
            return "off"

    def start(self):
        print("Turning on...")
        UI(id=1, cloud_status="startLoading").save()

        # Update desired task count
        self.ecs_client.update_service(cluster=self.cluster, service=self.service, desiredCount=1)
        print("Service desired task count updated!")

        serviceDescriptions = self.ecs_client.describe_services(cluster=self.cluster, services=[self.service])["services"]
        print(serviceDescriptions[0]["desiredCount"])

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
        UI(id=1, cloud_status=public_ip).save()

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

        self.ecs_client.update_service(cluster=self.cluster, service=self.service, desiredCount=0)
        print("Service desired task count updated!")

        serviceDescriptions = self.ecs_client.describe_services(cluster=self.cluster, services=[self.service])["services"]
        print(serviceDescriptions[0]["desiredCount"])

        UI(id=1, cloud_status="stopLoading").save()

        taskArns = self.ecs_client.list_tasks(cluster=self.cluster)["taskArns"]
        self.off_waiter.wait(cluster=self.cluster, tasks=[taskArns[0]])
        print("Task stopped.")
        UI(id=1, cloud_status="off").save()
