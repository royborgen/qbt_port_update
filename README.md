# qBittorrent Port Update

This repository contains a Python script designed to automate the integration between Gluetun and qBittorrent Docker containers. Specifically, the script fetches the forward port number from the Gluetun container's config location and updates the qBittorrent container's configuration to use this port.

The script is utilized alongside a cron job to execute daily, ensuring that the forward port is updated post any Watchtower-initiated container updates and restarts and server reboots.

## Workflow
The script automates the following tasks:

1. Read path to gluetun's forward_port file and qBitTorrent's qBittorrent.conf file.
2. Verify that the files exist
3. Execute: `docker stop qbittorrent`
4. Fetch port from `forwarded_port`
5. Reading qBittorrent.conf and fetch `Session\Port`
6. Compare the port from both files
7. Update `qBittorrent.conf` if needed.
8. Execute: `docker start qbittorrent`


## Installation

1. Clone or download the repository to your local machine.
2. Ensure you have the required Python dependencies installed:
    - Python 3 
    - configparser library installed 
    - os library installed 
    - subprocess library installed
3. Modify `port_update.conf` and set correct paths. 

## Optional Config
Instead of using `port_update.config`, you can set the needed configuration parameters as environment variables.
The file `setenvs.sh` contains all needed variables. Modify it as needed an execute the script by running 
`. ./setenvs.sh`. The leading dot (.) ensures that the script is sourced into the current shell session, making 
the environment avaialbe for the python script. 


## Usage 
The script is executed by running `qbt_port_update.py`


## Run in Docker container
```
docker run -d \
  --name qbt-port-update \
  -v /srv/qbt-port-update:/config \
  -v /srv/gluetun/forwarded_port:/config/gluetun/forwarded_port:rw \
  -v /srv/qBittorrent/qBittorrent.conf:/config/qBittorrent/qBittorrent.conf:rw \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e TZ=Europe/Oslo \
  -e QBT_CONTAINER_ID=qbittorrent \
  -e CREATE_LOG_FILE=yes \
  -e LOGTIMEFORMAT=%d-%m-%Y\ %H:%M:%S \
  -e CRON_SCHEDULE=*/15\ *\ *\ *\ * \
  --restart unless-stopped \
  royborgen/qbt-port-update:latest
```

Se `docker-compose.yaml` if you wish to use docker compose to start the container

### Supported enviroment variables
```
CREATE_LOG_FILE=yes/no
CRON_SCHEDULE=*/15 * * * *  
LOGFILE=/config/qbt_port_update.log
LOGTIMEFORMAT=%d-%m-%Y %H:%M:%S 
QBT_CONTAINER_ID=qbittorrent
PATH_GLUETUN=/config/gluetun/forwarded_port
PATH_QBITTORRENT=/config/qBittorrent/qBittorrent.conf
```

- `CREATE_LOG_FILE` should only container `yes` or `no`
- `CRON_SCHEDULE` require the use of correctly formated cron job. 
- `LOGTIMEFORMAT` controls the time format of the logfile. This can be adjusted to your liking. 
- `CONTAINER_ID` must container name or ID of the qBittorrent container you are running. This is needed so that we can restart the container. 
It is recommended to stay away from changing `PATH_GLUETUN` and `PATH_QBITTORRENT`. Instead of changing these you should edit the container volumes as this controls the location of the config file of the Gluetun and qBittorrent container. 


## Logging
The creates by default i logfile updates.log in the scripts directory. You can modify the path in the config file. 

Log sample: 
```
19-11-2024 23:32:18 - INFO - qBittorrent Port Update started...
19-11-2024 23:32:18 - INFO - Verifying the presence of /config/gluetun/forwarded_port
19-11-2024 23:32:18 - INFO - Found /config/gluetun/forwarded_port
19-11-2024 23:32:18 - INFO - Verifying the presence of /config/qBittorrent/qBittorrent.conf
19-11-2024 23:32:18 - INFO - Found /config/qBittorrent/qBittorrent.conf
19-11-2024 23:32:18 - INFO - Fetching port from /config/gluetun/forwarded_port
19-11-2024 23:32:18 - INFO - Forward port is 36072
19-11-2024 23:32:18 - INFO - Reading qBittorrent config file: /config/qBittorrent/qBittorrent.conf
19-11-2024 23:32:18 - INFO - Session\Port=46575
19-11-2024 23:32:18 - INFO - Forward port has changed! Updating qBittorrent.conf
19-11-2024 23:32:18 - INFO - Stopping container qbittorrent
19-11-2024 23:32:30 - INFO - Container successfully stopped!
19-11-2024 23:32:30 - INFO - Session\Port updated with value 36072
19-11-2024 23:32:30 - INFO - Starting container qbittorrent
19-11-2024 23:32:30 - INFO - Container successfully started!
19-11-2024 23:32:30 - INFO - qBittorrent Port Update completed
20-11-2024 02:34:25 - INFO - qBittorrent Port Update started...
20-11-2024 02:34:25 - INFO - Verifying the presence of /srv/gluetun/forwarded_port
20-11-2024 02:34:25 - INFO - Found /srv/gluetun/forwarded_port
20-11-2024 02:34:25 - INFO - Verifying the presence of /srv/qBittorrent/qBittorrent.conf
20-11-2024 02:34:25 - INFO - Found /srv/qBittorrent/qBittorrent.conf
20-11-2024 02:34:25 - INFO - Fetching port from /srv/gluetun/forwarded_port
20-11-2024 02:34:25 - INFO - Forward port is 36072
20-11-2024 02:34:25 - INFO - Reading qBittorrent config file: /srv/qBittorrent/qBittorrent.conf
20-11-2024 02:34:25 - INFO - Session\Port=36072
20-11-2024 02:34:25 - INFO - Forward port is unchanged! No changes made to qBittorrent.conf
20-11-2024 02:34:25 - INFO - qBittorrent Port Update completed
```
