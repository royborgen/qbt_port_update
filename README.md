# qBittorrent Port Update

This repository contains a Python script designed to automate the integration between Gluetun and qBittorrent Docker containers. Specifically, the script fetches the forward port number from the Gluetun container's config location and updates the qBittorrent container's configuration to use this port.

The script is utilized alongside a cron job to execute daily, ensuring that the forward port is updated post any Watchtower-initiated container updates and restarts.

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

3. Modify port_update.conf and set correct paths   
