# SorterBot Control Panel
*Note: This repository is still work in progress!*

Control Panel for the SorterBot project. It provides real-time monitoring and control capabilities to the robot arms connected to the system. This application does not do any computationally heavy tasks, so it can conveniently run on a t2.micro EC2 instance which is included in the AWS Free Tier. The arms only need to be configured to connect to the Control Panel, which can retreive the IP address of the Cloud service and send it to the arms.

### Usage
The UI shows a list of all of the arms ever connected to the system, each of them has a status LED, which blinks orange if the arm is online, but cannot connect to the SorterBot Cloud, while it blinks green if the arm is connected to the cloud service and ready to start a session. A session can be started by pressing the black play button on the selected arm. After a session is started, it will show up in the second column, where the logs will show up real-time as the arm proceeds with the session. The arm takes a set of pictures before and after the operations, which are stiched together and can be displayed by clicking the appropriate buttons within a session.

### Architecture
The project consists of a React frontend and a Django (Python) backend. It uses Django Channels (WebSockets) for real-time bi-directional communication. Django Channels require a Redis server as a backend, it is included in the Docker Compose as a separate image. It uses a PostgreSQL database, which is deployed to AWS in production.

### Development Locally
You can run SorterBot Control Panel in 3 modes: *local*, *aws-dev*, and *production*.
- **local**: No AWS resources are needed. ECS Manager functionality and S3 uploads are disabled. Postgres connection string and Django secret key are both retrieved from environment variables.
- **aws-dev**: S3 uploads are enabled, but ECS Manager is disabled. An RDS PostgreSQL instance is used for database, it's connection string is retrieved from the SSM parameter store. Django secret key is loaded from the environment.
- **production**: All functionality enabled, both postgres connection string and Django secret key are loaded from the SSM parameter store. Do not run in this mode locally, it is used on the EC2 instance when deployed to production.

1. Build Docker image
    ```
    docker build --build-arg MODE_ARG=local -t sorterbot_control .
    docker build \
        --build-arg MODE_ARG=local \
        --build-arg DEPLOY_REGION_ARG=eu-central-1 \
        -t sorterbot_control:latest .
    ```
1. Create a file named `.env` in the *sbc_server* folder, and set the same PostgreSQL connection string that you used for SorterBot Cloud under the key `PG_CONN`, and a long, random string under the key `DJANGO_SECRET`. In *local* mode, you need to specify both values, in *aws-dev* mode, you can omit PG_CONN. The result should look similar to this example:
    ```
    PG_CONN=postgresql://postgres:mypassword@172.17.0.2:5432/postgres
    DJANGO_SECRET=fJ2SmJNLsIDFXauoPIvKn1S3kDe6WVIdSrdiMsJq
    ```
1. Run image with Docker Compose

    Running `docker compose` will spin up two images, SorterBot Control Panel, and a Redis image, which is used by Django Channels, Django's websockets implementation.

    Django is running on port 8000 inside the container, you need to map that to an external port by setting it with the `EXT_PORT` environment variable. In *local* and *aws-dev* modes this should be 8000, in *production* mode, 80.

    You can specify mode assigning one of the 3 values mentioned above to the environment variable `MODE`. 
    
    On the first run, you need to set a truthy value to `MIGRATE`, which will execute the Django migrations. On later runs, you can omit this. Later on, if you modify the database structure, you need to run the migrations again.
    ```
    EXT_PORT=8000 MODE=[value] MIGRATE=1 docker-compose up
    ```
2. Start User Interface
   
    First `cd` to the *client* folder in the project root, then (only if you are running it for the first time), install the JavaScript dependencies:
    ```
    yarn
    ```
    After that, start the dev server with the following command:
    ```
    yarn start
    ```
    When the dev server started, you can access the UI in your browser under the following address: [http://localhost:3000](http://localhost:3000)


### Deploy to Production
You can deploy SorterBot Cloud to AWS as part of the SorterBot solution. Please refer to the [Production section of the SorterBot Installer](https://github.com/simonszalai/sorterbot_installer#production) repository's README.
