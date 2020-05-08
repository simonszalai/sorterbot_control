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
    1. In the AWS Console, go to **Services** > **RDS**.
    1. Click **Create database**.
    1. At creation method, keep **Standard Create** selected, then choose **PostgreSQL** as engine.
    1. Keep **Version** on the default value.
    1. Select **Free Tier** under templates.
    1. Under **DB Instance Identifier**, give the DB a name, like *sorterbot-postgres*.
    1. Leave **Master username** the default (*postgres*), and add a **Master password**.
    1. Leave the instance size on *db.t2.micro*, as this is the only one included in the Free Tier.
    1. Click on **Additional connectivity configuration**, then add a name to **Initial database name**, like *sorterbot*.
    1. Check *Yes* under **Publicly accessible**.
    1. Under **Database authentication** select *Password and IAM database authentication*.
    1. Click on **Additional configuration**, then uncheck **Enable automatic backups**, since storing backups costs money and it is not included in the Free Tier.
    1. Leave everything else on default, then click **Create database**.
    1. When the database is created, click on it's name, then on the **Connectivity & Security** tab, under **Security**, click on the name of the **VPC Security Groups**.
    1. After the security groups loaded, click on the ID of the security group that shows up, the click **Edit inbound rules**. You will find one existing rule, modify the **Source** of that to *Anywhere*. Click **Save rules**.
    1. Repeat the above for Outbound rules.
    1. To enable IAM authentication (which the Control Panel uses), you need to log in to the RDS instance. You can do that using a CLI tool from the EC2 instance that you created. 
        1. In the CLI of the EC2 instance, install psql:
            ```
            sudo amazon-linux-extras install postgresql11
            ```
        1. Connect to the postgres instance:
            ```
            psql -h [HOSTNAME] -p [PORT] -U [USERNAME] -W
            ```
            The command should look similar to this:
            ```
            psql -h sorterbot-postgres.ct2v58jbu37d.eu-central-1.rds.amazonaws.com -p 5432 -U postgres -W
            ```
            Then type the master password, for the DB.
        1. Now you are logged in to the postgres instance. You need to add *postgres* user to the *rds_iam* permission group:
            ```
            GRANT rds_iam to postgres;
            ```
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