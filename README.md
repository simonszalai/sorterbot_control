# SorterBot Control Panel
This is the repository for the Control Panel of my SorterBot project. It provides real-time monitoring and control capabilities to the robot arms connected to the system. This application does not do any computationally heavy tasks, so it can conveniently run on a t2.micro EC2 instance which is included in the AWS Free Tier. The arms only need to be configured to connect to the Control Panel, which can retreive the IP address of the Cloud service and send it to the arms. In this 

#### Usage
The UI shows a list of all of the arms ever connected to the system, each of them has a status LED, which blinks orange if the arm is online, but cannot connect to the SorterBot Cloud, while it blinks green if the arm is connected to the cloud service and ready to start a session. A session can be started by pressing the black play button on the selected arm. After a session is started, it will show up in the second column, where the logs will show up real-time as the arm proceeds with the session. The arm takes a set of pictures before and after the operations, which are stiched together and can be displayed by clicking the appropriate buttons within a session.

#### Tech Stack
It consists of a React front-end and a Django (Python) back-end. It uses Django Channels (WebSockets) for real-time bi-directional communication. Django Channels requires a Redis server as a back-end, it is included in the Docker Compose as a separate image. It uses a postgreSQL database deployed to AWS.

### Run SorterBot Control Panel locally
1. Clone repository.
1. Build Docker image:
    ```
    docker build -t sorterbot_control .
    ```
1. Run image with Docker Compose:
    ```
    docker-compose up
    ```

### Deploy SorterBot Control Panel to AWS
Here you can find the instructions how to manually create the neccessary resources to deploy SorterBot Control Panel to AWS. Since this is a quite long list, the recommended way of deploying is by using the SorterBot Installer, which automates most of these steps.


1. This application also needs a PostgreSQL database. Follow these steps to create one and deploy it on AWS RDS:
   
1. Run the application using Docker Compose after changing the working directory to *sorterbot_control*:
    ```
    cd sorterbot_control
    docker-compose up
    ```
    If this is the first time you are launching SorterBot Control Panel, you need to apply Django Migrations to the database. You can do that by modifying the command this way: 
    ```
    MIGRATE=1 docker-compose up
    ```
    If you are not sure, apply the migrations, it will not cause any problems even if you applied them before.





```
aws ec2 create-key-pair --key-name sorterbot --query 'KeyMaterial' --output text > ~/.aws/ssh_sorterbot_ec2.pem
```