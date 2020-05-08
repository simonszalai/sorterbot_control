## Deploy SorterBot to AWS
Following the steps below you can deploy the whole SorterBot solution to AWS Cloud. Most of the resources are within the Free Tier, and those that are not, most likely won't incur costs more than a few dollars per month. Since this is a very long and cumbersome process, so I created an installer to automate most of these steps, which you can find in the SorterBot Installer repository. If you want to understand in detail what the installer is doing, it might be a good idea to follow these steps and deploy the resources manually.
### Networking
Before we can start deploying the actual resources needed for the SorterBot system, we need to create a Virtual Private Cloud to manage security and networking.
#### Create a VPC
1. Go to **Services** > **VPC** then click the **Create VPC** button.
1. Give it a name, like *sorterbot-vpc*.
1. Specify an IP range, like *10.0.0.0/16*. This means that the first 16 bits (2 numbers, 10 and 0 here) are fixed, and the rest can be freely distributed within the VPC. That means the VPC can have 65 535 different IP addresses ranging from 10.0.0.0 to 10.0.255.255.
1. Leave the rest on default and click **Create**.

#### Create subnets
We need to create 2 subnets, a public and a private. To do that, still on the VPC Dashboard:
1. Click on **Subnets** on the left, then click **Create subnet**.
1. Give it a name, like *sorterbot-private-subnet*, select the VPC previously created, and to **IPv4 CIDR block** write a narrower IP range than the VPC, for example, *10.0.0.0/24*. Click **Create**.
1. Repeat the above step to create a public subnet, and name it like *sorterbot-public-subnet*. For **IPv4 CIDR block**, choose another IP range, which is not overlapping with the private subnet, like 10.0.1.0/24. Click **Create**.

#### Enable Internet Access for the VPC
To enable Internet access, we need to create an Internet Gateway, attach it to our VPC and and set up a custom route table. To do that, still in the VPC Console:
1. On the left sidebar, click **Internet Gateways**, then choose **Create internet gateway**.
1. Name the gateway, like *sorterbot-internet-gateway*, then click **Create**.
1. Select the gateway you just created, click **Actions** > **Attach to VPC**, then select the VPC you created above, and finally click **Attach**.
1. On the left, click on **Route Tables**. There will be already a route table here automatically created together with the VPC. It won/t have a name, but for clarity, you can name it to something like *sorterbot-route-table*.
1. Select the Route table, and on the **Routes** tab at the bottom, click **Edit routes**, then **Add route**.
1. As **Destination**, type *0.0.0.0/0* (which represents all addresses and ports), and as **Target**, first select *Internet Gateway*, then click on the internet gateway you previously created. Finally click **Save routes**.
1. On the **Subnet Associations** tab, click **Edit subnet associations**, select your PUBLIC subnet, then click **Save**.

### SorterBot Control Panel
1. Go to AWS Console > Services > EC2 and click **Launch Instance**.
1. Select **Amazon Linux 2 AMI**.
1. Select **t2.micro** instance type as it is included in the Free Tier, then click **Next: Configure Instance Details**.
1. Leave everything on default and click **Next: Add Storage**, then **Next: Add Tags**, then **Next: Configure Security Group**.
1. Give the security group a sensible name and description, like *sorterbot-control-security-group*.
1. In the only existing rule with **Type** *SSH*, change **Source** to *Anywhere*.
1. Add the following rules:

    | Type          | Port Range | Source   |
    | ------------- | ---------- | -------- |
    | PostgreSQL    | 5432       | Anywhere |
    | Custom TCP    | 8000       | Anywhere |
    | HTTP          | 80         | Anywhere |

1. Click **Review and Launch** then **Launch**.
1. In the pop-up window, select *Create a new key pair*, give it a sensible name, like *sorterbot-control-ssh-key*, then click **Download Key Pair**.
1. After the key is downloaded, click **Launch Instances** then **View Instances**.
1. Select the newly created instance and copy **Public DNS (IPv4)**, which can be found in the instance's description at the top of the right column.
1. In order for the SSH key to work, the permissions needs to be changed to read only. Open the Terminal and write:
    ```
    chmod 400 /path/my-key-pair.pem
    ```
1. After this, you can SSH into the instance using a command like this:
    ```
    ssh -i /path/my-key-pair.pem ec2-user@ec2-198-51-100-1.compute-1.amazonaws.com
    ```
    Change *"/path/my-key-pair.pem"* to the path of your downloaded key and change *"<span>ec2-198-51-100-1.compute-1.amazonaws.</span>com"* to your instance's DNS that you just copied. Notice **ec2-user@** in the command which corrensponds to the default username and it is not part of the DNS that you copy from the AWS Console!
1. Execute the following commands to install dependencies:
    ```
    # Update repositories
    sudo yum update -y

    # Install Docker and Git
    sudo yum install docker git -y

    # Download and Install Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/download/1.25.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

    # Make the Docker Compose binary executable
    sudo chmod +x /usr/local/bin/docker-compose

    # Download Git Large File Storage (used for some static web assets in the repository)
    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | sudo bash

    # Install Git LFS
    sudo yum install git-lfs -y
    git lfs install
    ```
1. Clone SorterBot Control repository:
    ```
    git clone https://github.com/simonszalai/sorterbot_control.git
    ```
1. Start Docker service:
    ```
    sudo service docker start
    ```
1. Add current user to the Docker group:
    ```
    sudo usermod -a -G docker ec2-user
    ```
1. Log out an in again to re-evaluate group membership settings. You can do that by exiting the SSH session with the `exit` command and logging in again the same way as before. Note that in some cases it might be needed to reboot your instance from EC2 Console.
1. Build Docker image and tag it as *sorterbot_control:latest*:
    ```
    docker build -t sorterbot_control:latest sorterbot_control
    ```
1. To provide the neccessary permissions for the Control Panel to work properly, follow these steps:
   1. In the AWS Console, go to  Services > IAM
   1. Go to **Policies** and click **Create policy**
   1. Click on the **JSON** tab and paste the following code:
        ```
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": [
                        "ecs:ListServices",
                        "ecs:UpdateService",
                        "ec2:DescribeNetworkInterfaces",
                        "ecs:ListTasks",
                        "ecs:DescribeServices",
                        "ecs:DescribeTasks",
                        "ecs:ListClusters",
                        "rds-db:connect"
                    ],
                    "Resource": "*"
                }
            ]
        }
        ```
        These are the minimal permissions needed for the Control Panel to function properly, and nothing more. It will enable it to get and set the status of the ECS Cluster where the SorterBot Cloud service runs and also allows the Django backend to retrieve temporary passwords for IAM authentication with the postgres database running on RDS.  
        After done, click **Review Policy**.
    1. Give the policy a sensible name (and optionally a description), like *SorterBotControlPolicy*, then click **Create policy**.
    1. Go to **Roles** and click **Create Role**
    1. Choose **EC2** as Use Case, then click **Next: Permissions**
    1. In the search field, write the name of the newly created policy (e.g. *SorterBotControlPolicy*)
    1. Select the policy, then click **Next: Tags** then **Next: Review**.
    1. Give the role a name, like *SorterBotControlRole* and click **Create role**
    1. Go to the EC2 dashboard, click **Instances** in the left sidebar and select the instance that you created earlier.
    1. Click on **Actions** > **Instance Settings** > **Attach/Replace IAM role**
    1. Select the role that you just created (e.g. *SorterBotControlRole*) then click **Apply**.