## Deploy SorterBot to AWS
Following the steps below you can deploy the whole SorterBot solution to AWS Cloud. Most of the resources are within the Free Tier, and those that are not, most likely won't incur costs more than a few dollars per month. Since this is a very long and cumbersome process, so I created an installer to automate most of these steps, which you can find in the SorterBot Installer repository. If you want to understand in detail what the installer is doing, it might be a good idea to follow these steps and deploy the resources manually.
### Networking
Before we can start deploying the actual resources needed for the SorterBot system, we need to create a Virtual Private Cloud to manage security and networking.
#### Create a VPC
1. Go to **Services** > **VPC** then click the **Create VPC** button.
1. Give it a name, like *sorterbot-vpc*.
1. Specify an IP range, like *10.0.0.0/16*. This means that the first 16 bits (2 numbers, 10 and 0 here) are fixed, and the rest can be freely distributed within the VPC. That means the VPC can have 65 535 different IP addresses ranging from 10.0.0.0 to 10.0.255.255.
1. Leave the rest on default and click **Create**.
1. To enable DNS names, select the newly created VPC, click **Actions** > **Edit DNS hostnames**, *enable* **DNS hostnames**, then click **Save**.

#### Create subnets
We need to create at least 2 public subnets in different availablity zones (as per RDS requirements). To do that, still on the VPC Dashboard:
1. Click on **Subnets** on the left, then click **Create subnet**.
1. Give it a name, like *sorterbot-public-subnet-a*, select the VPC previously created, and under **Availability Zone**, select the first entry. To **IPv4 CIDR block**, write a narrower IP range than the VPC, for example, *10.0.0.0/24*. Click **Create**.
1. Repeat the above stepat least once to create another public subnet, and name it like *sorterbot-public-subnet-b*. For **IPv4 CIDR block**, choose another IP range, which is not overlapping with the first subnet, like 10.0.1.0/24. Click **Create**.

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
SorterBot Control Panel needs two resources, both of them included in the Free Tier: a Django application running on an EC2 instance and a PostgreSQL database running on an RDS instance.
#### EC2 Instance
1. Go to AWS Console > **Services** > **EC2** and click **Launch Instance**.
1. Select **Amazon Linux 2 AMI**.
1. Leave *t2.micro* selected as instance type, since it is the only one included in the Free Tier, then click **Next: Configure Instance Details**.
1. Under **Subnet**, change the value to the public subnet (e.g. *sorterbot-public-subnet*) that you created earlier.
1. *Enable* **Auto-assign Public IP**.
1. Leave the rest on default and click **Next: Add Storage**, then **Next: Add Tags**, then **Next: Configure Security Group**.
1. Give the security group a sensible name and description, like *sorterbot-control-security-group*.
1. Make sure that the following rules are added:

    | Type          | Port Range | Source   |
    | ------------- | ---------- | -------- |
    | SSH           | 22         | Anywhere |
    | PostgreSQL    | 5432       | Anywhere |
    | Custom TCP    | 8000       | Anywhere |
    | HTTP          | 80         | Anywhere |

1. Click **Review and Launch** then **Launch**.
1. In the pop-up window, select *Create a new key pair*, give it a sensible name, like *sorterbot-control-ssh-key*, then click **Download Key Pair**. After the key is downloaded, click **Launch Instances**, then **View Instances**.
1. In order for the SSH key to work, the permissions needs to be changed to read only. Open the Terminal and execute the following command: (change the path/filename to match the location of your downloaded key if needed)
    ```
    chmod 400 ~/Downloads/sorterbot-control-ssh-key.pem
    ```
1. Select the newly created instance, wait until it boots up, then copy **Public DNS (IPv4)**, which can be found in the instance's description at the top of the right column.
1. Now you can SSH into the instance using a command like this:
    ```
    ssh -i ~/Downloads/sorterbot-control-ssh-key.pem ec2-user@[EC2_PUBLIC_DNS]
    ```
    Change the path of your downloaded key if needed, and change *[EC2_PUBLIC_DNS]* to your instance's DNS that you just copied. Notice **ec2-user@** in the command which corrensponds to the default username and it is not part of the DNS that you copy from the AWS Console!
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
    Note that if you copy-paste the code cell above, the last command will not be executed, you need to press enter at the end to execute the last command.
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
#### PostgreSQL Database
While the Docker image is building, you can create the PostgreSQL database:
1. In the AWS Console, go to **Services** > **RDS**.
1. Click **Create database**.
1. At **Choose a database creation method**, keep *Standard Create* selected, then choose *PostgreSQL* at **Engine options**.
1. Keep **Version** on the default value (*PostgreSQL 11.5-R1*) If the default changes in the future, make sure that you select a version with 11 as main version.
1. Select *Free Tier* under **Templates**.
1. Under **DB Instance Identifier**, give the DB a name, like *sorterbot-postgres*.
1. Leave **Master username** the default (*postgres*), and add a **Master password**.
1. Leave the **DB instance class** on *db.t2.micro*, as this is the only one included in the Free Tier.
1. Make sure that under **Virtual private cloud (VPC)** that VPC is selected that you created above (e.g. *sorterbot-vpc*).
1. Click on **Additional connectivity configuration**, then select *Yes* under **Publicly accessible**.
1. Under **VPC security group**, select *Create new*, and give it a name, for example *sorterbot-postgres-security-group*.
1. Under **Database authentication** select *Password and IAM database authentication*.
1. Click on **Additional configuration**, then add a name to **Initial database name**, like *sorterbot*.
1. Uncheck **Enable automatic backups**, since storing backups costs money and it is not included in the Free Tier.
1. Leave everything else on default, then click **Create database**.
1. When the database is created, click on it's name, then on the **Connectivity & Security** tab, under **Security**, click on the name of the **VPC Security Groups**.
1. After the security groups loaded, click on the ID of the security group that shows up, the click **Edit inbound rules**. You will find one existing rule, modify the **Source** of that to *Anywhere*. Click **Save rules**.
1. To enable IAM authentication (which the Control Panel uses), you need to log in to the RDS instance. You can do that using a CLI tool from the EC2 instance that you created. 
    1. In the CLI of the EC2 instance, install psql:
        ```
        sudo amazon-linux-extras install postgresql11 -y
        ```
    1. Connect to the postgres instance:
        ```
        psql -h [HOSTNAME] -p [PORT] -U [USERNAME] -W
        ```
        The command should look similar to this:
        ```
        psql -h sorterbot-postgres.ct2v58jbu37d.eu-central-1.rds.amazonaws.com -p 5432 -U postgres -W
        ```
        Then type the master password you set above for the DB.
    1. Now you are logged in to the postgres instance. You need to add *postgres* user to the *rds_iam* permission group. Execute the following command:
        ```
        GRANT rds_iam to postgres;
        ```
    1. You can quit the session by typing `\q`.
1. Finally, to enable SorterBot Cloud to access the database, you need to store a connection string in the AWS Parameter Store, which can be loaded later as an environment variable. To do that:
    1. Go to **Services** > **Systems Manager**.
    1. On the left, click on **Parameter Store**.
    1. Click on **Create parameter**.
    1. Enter a name, for example *SorterBotCloudPostgres*.
    1. Change **Type** to *SecureString*.
    1. Add the connection string to **Value**, conforming to the following structure:
        ```
        postgresql://[MASTER_USERNAME]:[MASTER_PASSWORD]@[RDS_ENDPOINT]:[PORT]/[DBNAME]
        ```
        For example:
        ```
        postgresql://postgres:goA4faSeBp8YYfr4elJu@sorterbot-postgres.ct1v28hgu37d.eu-central-1.rds.amazonaws.com:5432/sorterbot
        ```
    1. Click on **Create parameter**.
#### IAM Permissions
   1. In the AWS Console, go to **Services** > **IAM**.
   1. Go to **Policies** and click **Create policy**.
   1. Click on the **JSON** tab and replace the code there with the following:
        ```
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": [
                        "ec2:DescribeNetworkInterfaces",
                        "ecs:*"
                    ],
                    "Resource": "*"
                }
            ]
        }
        ```
        These are the minimal permissions needed for the Control Panel to function properly, and nothing more. It will enable it to get and set the status of the ECS Cluster where the SorterBot Cloud service runs and also allows the Django backend to retrieve temporary passwords for IAM authentication with the postgres database running on RDS.  
        After done, click **Review Policy**.
    1. Give the policy a sensible name (and optionally a description), like *SorterBotControlPolicy*, then click **Create policy**.
    1. Go to **Roles** and click **Create Role**.
    1. Under **Select type of trusted entity** click *AWS service*, under **Choose a use case**, select *EC2*, then click **Next: Permissions**.
    1. In the search field, write the name of the newly created policy (e.g. *SorterBotControlPolicy*), then select the policy you just created, and finally click **Next: Tags**, then **Next: Review**.
    1. Give the role a name, like *SorterBotControlRole* and click **Create role**.
    1. Go to the EC2 dashboard, click **Instances** in the left sidebar and select the instance that you created earlier.
    1. Click on **Actions** > **Instance Settings** > **Attach/Replace IAM role**.
    1. Select the role that you just created (e.g. *SorterBotControlRole*) then click **Apply**.

### SorterBot Cloud
SorterBot Cloud service does the image processing, so it needs morepowerful hardware, which should also be scaalble in case there are more arms connected to the system. Also, there is a GitHub Actions CI pipeline for this service, so in case the code or the model weights change, it can be redeployed with a single click. To make these features possible, SorterBot Cloud needs to be deployed to Elastic Container Service. To store the Docker images, an Elastic Container Registry is also needed. These services are outside of the Free Tier, so make sure to shut them down when they are not in use. I also recommend delete old Docker images from ECR, as they are priced per GB per month, and the images are quite big (more than 4 GB).

#### Create IAM user and roles
##### Create Service Role for the Docker container
This role will be attached to the ECS Tasks and will enable SorterBot Cloud to access S3.
1. In the AWS Console, go to **Services** > **IAM**.
1. Click on **Policies**, then **Create policy**.
1. Paste the following code to the **JSON** tab:
    ```
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ssm:GetParameters",
                    "secretsmanager:GetSecretValue",
                    "kms:Decrypt"
                ],
                "Resource": [
                    "*"
                ]
            }
        ]
    }
    ```
1. Click **Review policy**, name it like *SecretsForECSPolicy*, then click **Create policy**.
1. Click to **Roles**, then **Create role**.
1. Under **Select type of trusted entity**, select *AWS service*.
1. Under **Or select a service to view its use cases** select *Elastic Container Service*, then under **Select your use case**, select *Elastic Container Service Task* (note task at the end!), then click **Next: Permissions**.
1. Select *AmazonS3FullAccess*, *AmazonECSTaskExecutionRolePolicy* and *SecretsForECSPolicy* (the policy you just created) from the list, then click **Next: Tags**, **Next: Review**, name your role something like *SorterBotCloudServiceRole*, and click **Create role**.

##### Create IAM user for building and pushing the Docker image
To build the Docker image, you will need the trained weights, which are stored in an S3 bucket. Other than that, you need to authorize pushing the Docker image to the ECR registry. Follow these steps to create and set an IAM user that will enable these actions:

1. Click on **Policies**, then **Create policy**.
1. Under **Service**, select *Elastic Container Registry*, and under **Actions**, select *All Elastic Container Registry actions (ecr:*)*.
1. Click **Review**, name it something like *SorterBotCloudECR*, then click **Create policy**.
1. Click on **Users**, then **Add user**.
1. Give the user a name, like *SorterBotCloudUser* and select *Programmatic access* as **Access type**.
1. Click **Next: Permissions**, under **Set permissions** click *Attach existing policies directly*, then select the permission that you just created. Also select *AmazonS3FullAccess*. Finally click **Next: Tags**, **Next: Review**, then **Create user**. Do NOT click on **Close**!
1. Open the following file (if it doesn't exist, create it):
    ```
    ~/.aws/credentials
    ```
1. Add a new entry to the file, which will look like the following:
    ```
    [sorterbotcloud]
    aws_access_key_id=AKIAX2J3SYTEXFBBJIZK
    aws_secret_access_key=7C9NGG2OTbcxnKtB4XHo8pEZKCckjrHn9bremVPw
    ```
    Replace the key ID and the secret to the values you got after creating the IAM user. In the first line, it is a profile name, which you will need to reference later when using the credentials. Save and exit the file.
1. In the same folder, open (or create) another file named `config` (without extension). Here you need to specify the region. in the square brackets use the same profile name that you used for the credentials. The entry that you need to add will look similar to this:
    ```
    [profile sorterbotcloud]
    region=eu-central-1
    ```
    Note the usage of `profile` here, but not at credentials! Save and exit the file.
1. Now you can close the window from which you copied the credentials.

#### Elastic Container Registry (ECR)
##### Create Repository
1. Go to **Services** > **Elastic Container Registry**, then click on **Create repository**.
1. Give the repository a name, like *sorterbot_cloud*, then click **Create repository**.

##### Upload Docker image to the respository
1. Download and install AWS CLI tools by running the following commands (change the region if you are using a different one):
    ```
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    ./aws/install
    aws configure set region eu-central-1
    ```
1. Clone the SorterBot Cloud repository, and in the root folder of the project, build the Docker image and tag it with the URI of your ECR repository:
    ```
    DOCKER_BUILDKIT=1 docker build -t 537539036361.dkr.ecr.eu-central-1.amazonaws.com/sorterbot-ecr --secret id=aws_config,src=/Users/simon/.aws/config --secret id=aws_credentials,src=/Users/simon/.aws/credentials .
    ```
    In the above command, Docker BuildKit's mount feature is used to provide credentials to authenticate with S3 during build. (It is needed to download the trained model weights). This way the credentials are only available for that single command, and will not end up in the final image.
1. Authenticate with the ECR repository. Notice `sorterbotcloud` after `--profile`, which corresponds to the profile name that you saved the credentials with. Change it here if you used a different name.
    ```
    aws ecr get-login-password --region eu-central-1 --profile sorterbotcloud | docker login --username AWS --password-stdin 537539036361.dkr.ecr.eu-central-1.amazonaws.com/sorterbot-ecr
    ```
1. Push the image you just built to the ECR repository:
    ```
    docker push 537539036361.dkr.ecr.eu-central-1.amazonaws.com/sorterbot-ecr
    ```
1. While the image is uploading, start creating the ECS resources.

#### Elastic Container Service (ECS)
Since the Control Panel interacts with the ECS resources below, to unambigously identify them, tags needs to be added, with SDIB keys. This way retrieving the correct resource does not depend on names, and resources can be named anything as long as the tags match.
##### Create a Cluster
1. Go to **Services** > **Elastic Container Service**, then click **Clusters** on the left, then **Create Cluster**.
1. Select *Networking only*, then click **Next step**.
1. Give the cluster a name, like *sorterbot-cluster*, make sure that Create VPC is NOT checked, add a tag with key: *SBID* and value: *SBCluster*, then click **Create**, and finally on **View cluster**.
##### Create a Task Definition
1. On the laft pane, click **Task Definitions**, then **Create new Task Definition**.
1. Choose *Fargate* launch type, then click **Next step**.
1. Enter a name (e.g. *sorterbot-cloud-taskdef*).
1. Next to **Task role**, choose the service role for the Docker image that you created above (e.g. *SorterBotCloudServiceRole*).
1. Under **Task execution IAM role** select the same service role (e.g. *SorterBotCloudServiceRole*).
1. Set **Task memory (GB)** to *4 GB* and **Task CPU (vCPU)** to *0.5vCPU*.
1. Click **Add container**.
1. Name the image, like *sorterbot-cloud-image*.
1. In the text box under, next to **Image**, paste the URI of the uploaded image. You can find it in the **Image URI** column of your ECR repository.
1. Add a **Port mapping** with the following value: *6000*, and click **Add**.
1. Under **Environment variables**, add an entry with *PG_CONN* as key, change the dropdown to *ValueFrom* to retrieve the value from AWS Parameter Store, and enter the parameter name to the value field (e.g. SorterBotCloudPostgres). Note that this only works if the parameter store and the Task Definition are in the same region, otherwise you have to specify the full ARN to valueFrom.
1. Click **Create** to create your Task Definition.
##### Create a Service
1. In the main ECS panel, click on **Clusters** on the left side, select the cluster that you recently created, then on the **Services** tab, click **Create**.
1. For **Launch Type**, select *FARGATE*, select the Task Definition that you created above (e.g. *sorterbot-cloud-taskdef*), name your service something like *sorterbot-cloud-service*, then next to **Number of tasks**, write 1. Later, if you want to temporarily disable your service to save money, this is the number that you need to change to 0. Finally, click **Next step**.
1. Make sure that the VPC you created for this application is selected (e.g. *sorterbot-vpc*), select both of your PUBLIC subnets that belong to the selected VPC.
1. If you leave **Security groups** on default, a new one will be automatically created, but it is recommended to click on **Edit**, and give it a more descriptive name, like *sorterbot-cloud-security-group*.
1. Make sure that **Auto-assign public IP** is *ENABLED*.
1. Uncheck **Enable service discovery integration** and click **Next step**.
1. Click **Next step** again, review your settings and click **Create service**.
1. Click **View service**, and verify that on the **Tasks** tab, the task with *PENDING* status eventually turns to *RUNNING*. This might take a few minutes.
1. Click on the name of the service, then under **Network access**, click  on **Security groups**.
1. On the **Inbound rules** tab, click on **Edit rules**.
1. To enable the Raspberry Pi to directly access the Cloud service, Add a new rule with **Type** *custom TCP Rule*, **Port Range** 6000, and **Source** *Anywhere*. Click on **Save rules**.
