# qBittorrent Port Update
This repository contains a Python script that reads the `forwarded_port` file generated by Gluetun and checks if it matches the listening port listed in `qBittorrent.conf`. If there is a discrepancy, the script will stop the qBittorrent container, update the `qBittorrent.conf` file with the new port, and restart qBittorrent.

The script is best utilized alongside a cron job, which can be scheduled to run daily. This ensures that the forwarded port is updated after any Watchtower-initiated container updates, restarts, or server reboots.

## Backgroud

Most VPN providers do not allow setting a static forwarded port, causing the forwarded port to change each time Gluetun restarts. This script helps keep qBittorrent updated with the latest port, ensuring it remains connectable.


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
    - docker library installed
3. Modify `port_update.conf` and set correct paths. 

## Optional Config
Instead of using `port_update.config`, you can set the needed configuration parameters as environment variables.
The file `setenvs.sh` contains all needed variables. Modify it as needed an execute the script by running 
`. ./setenvs.sh`. The leading dot (.) ensures that the script is sourced into the current shell session, making 
the environment available for the python script. 


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
GLUETUN_IP=127.0.0.1
GLUETUN_PORT=8000
LOGFILE=/config/qbt_port_update.log
LOGTIMEFORMAT=%d-%m-%Y %H:%M:%S 
PATH_GLUETUN=/config/gluetun/forwarded_port
PATH_QBITTORRENT=/config/qBittorrent/qBittorrent.conf
PUID=1000
PGID=1000
TZ=Europe/Oslo
QBT_CONTAINER_ID=qbittorrent
```

- `CREATE_LOG_FILE` should only container `yes` or `no`
- `CRON_SCHEDULE` require the use of correctly formated cron job. 
- `GLUETUN_IP` Required from Gluetun 4.0.0. Needs to contain Gluetun server IP.  
- `GLUETUN_PORT` is requered from Gluetun v.4.0.0. Need to contain the Gluetun Control Server listening port. `Default port is 8000`. 
- `LOGTIMEFORMAT` controls the time format of the logfile. This can be adjusted to your liking. 
- `CONTAINER_ID` must container name or ID of the qBittorrent container you are running. This is needed so that we can restart the container.
- `TZ` allows you to set the time zone displayed in the log. For a complete overview of timezones, see the section `TZ identifiers` on [list of tz database time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) available on Wikipedia.
- `PUID` and `PGID` allow you to control which user and group that owns the config folder and the `qbt_port_update.log` file. If not provided, the default value of `0` (root) is used, ensuring that only the root user has ownership and access. This is ideal when running containers with different users on the system to avoid conflicting ownership. If you want to assign ownership to a specific non-root user (e.g., `1000`), you can provide the respective PUID and PGID values.

>[Note]<br>
>Control Server IPStarting from Gluetun v.4.0.0, the forwarded_port file will be deprecated. From this version we must fetch the forwarded port from the Gluetun Control Server. See [Gluetun GitHub](https://github.com/qdm12/gluetun-wiki/blob/main/setup/>advanced/vpn-port-forwarding.md) for more information. The feature is already implemented in qBittorrent Port Update. 

>**_CAUTION:**
If you are running qBittorrent Port Update in docker, it is recommended leave `PATH_GLUETUN` and `PATH_QBITTORRENT` with their default value. Instead of changing these you should edit the container volumes as these control the location of the qBittorrent config file and the Gluetun forwarded_port filer. 


## Logging
The creates by default i logfile updates.log in the scripts directory. You can modify the path in the config file. 

Log sample: 
```
------------------------------------------------------------------------------------------------------
qBittorrent Port Update
v.2.1.0
CREATE_LOG_FILE=yes
CRON_SCHEDULE=*/15 * * * *
GLUETUN_IP=127.0.0.1
GLUETUN_PORT=8000
LOGFILE=/config/qbt_port_update.log
LOGTIMEFORMAT=%d-%m-%Y %H:%M:%S
PATH_GLUETUN=/config/gluetun/forwarded_port
PATH_QBITTORRENT=/config/qBittorrent/qBittorrent.conf
QBT_CONTAINER_ID=qbittorrent
TZ=Europe/Oslo
------------------------------------------------------------------------------------------------------
23-11-2024 02:02:18 - INFO - qBittorrent Port Update started...
23-11-2024 02:02:18 - INFO - Fetching forwarded port from Gluetun Control Server on IP: 10.0.0.9:8001
23-11-2024 02:02:18 - INFO - Forwarded port is 43253
23-11-2024 02:02:18 - INFO - Reading qBittorrent config file: /config/qBittorrent/qBittorrent.conf
23-11-2024 02:02:18 - INFO - Session\Port=62080
23-11-2024 02:02:18 - INFO - Forwarded port has changed! Updating qBittorrent.conf
23-11-2024 02:02:18 - INFO - Stopping container qbittorrent
23-11-2024 02:02:28 - INFO - Container successfully stopped!
23-11-2024 02:02:28 - INFO - Session\Port updated with value 43253
23-11-2024 02:02:28 - INFO - Starting container qbittorrent
23-11-2024 02:02:29 - INFO - Container successfully started!
23-11-2024 02:02:29 - INFO - qBittorrent Port Update completed
```
