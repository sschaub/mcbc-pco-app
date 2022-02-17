# Setup

The following instructions assume you are using a Ubuntu 20 environment.

## Install Docker

Execute the following to install Docker:

```
sudo apt install docker.io
```

Execute the following to add the current user to the docker group so that docker commands can be executed without using sudo:


```
sudo usermod -a -G docker $USER
```

Logout, then login to make the change take effect. 

## Cloudflare Integration

The following procedure will enable Cloudflare integration, so that when the server boots
it automatically registers its IP address with Cloudflare:

Create /home/ubuntu/cloudflare.config:

```
cloudflare_auth_key=(Cloudflare API token)
```

Install cloudflare service and enable:

```
sudo cp cloudflare.service /etc/systemd/system
cd /etc/systemd/system
sudo systemctl enable cloudflare
```
## Application Installation

Execute the following to install the application:

First, clone the app to the ubuntu home directory:
```
cd ~
git clone https://github.com/sschaub/mcbc-pco-app
```

Next, run the process to generate the application HTML deployment bundle:
```
cd ~/mcbc-pco-app
. buildui
```

Next, install the database:
```
mkdir ~/mcbc-pco-app/db
```

Copy mcbcmusic.sqlite3 to ~/mcbc-pco-app/db

Next, create .env file in ~/mcbc-pco-app. See [Development Readme](../README-dev.md) for details.

## Application Startup

Finally, start the app:

```
cd ~/mcbc-pco-app
docker-compose --profile=prod up -d
```

This will set the application to start automatically on reboot.
