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
3. Modify `port_update.conf` and set correct paths


## Usage 
The script is executed by running `qbt_port_update.py`

## Logging
The creates by default i logfile updates.log in the scripts directory. You can modify the path in the config file. 

Log sample: 
```
08-04-2024 20:51:48 - INFO - Verifying the presence of /srv/gluetun/forwarded_port
08-04-2024 20:51:48 - INFO - Found /srv/gluetun/forwarded_port
08-04-2024 20:51:48 - INFO - Verifying the presence of /srv/qBittorrent/qBittorrent.conf
08-04-2024 20:51:48 - INFO - Found /srv/qBittorrent/qBittorrent.conf
08-04-2024 20:51:48 - INFO - Fetching port from /srv/gluetun/forwarded_port
08-04-2024 20:51:48 - INFO - Forward port is 53573
08-04-2024 20:51:48 - INFO - Reading qBittorrent config file: /srv/qBittorrent/qBittorrent.conf
08-04-2024 20:51:48 - INFO - Session\Port=51028
08-04-2024 20:51:48 - INFO - Forward port has changed! Updating qBittorrent.conf
08-04-2024 20:51:48 - INFO - Executing: docker stop qbittorrent
08-04-2024 20:51:54 - INFO - Container stop successful
08-04-2024 20:51:54 - INFO - Execution output: qbittorrent
08-04-2024 20:51:54 - INFO - Session\Port updated with value 53573
08-04-2024 20:51:54 - INFO - Executing: docker start qbittorrent
08-04-2024 20:51:55 - INFO - Container start successful
08-04-2024 20:51:55 - INFO - Execution output: qbittorrent
```
