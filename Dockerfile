# Use an official Debian Bookworm image
FROM debian:trixie-slim

# Install cron, Python, and other necessary dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y cron python3 python3-venv python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Set up a virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir docker

# Create the config directory
RUN mkdir -p /config

# Copy the Python script into the container
COPY qbt_port_update.py /usr/local/bin/qbt_port_update.py
RUN chmod 0644 /usr/local/bin/qbt_port_update.py

# Set environment variables
ENV PATH_GLUETUN=/config/gluetun/forwarded_port \
    PATH_QBITTORRENT=/config/qBittorrent/qBittorrent.conf \
    QBT_CONTAINER_ID=qbittorrent \
    CREATE_LOG_FILE=yes \
    LOGFILE=/config/qbt_port_update.log \
    LOGTIMEFORMAT="%d-%m-%Y %H:%M:%S"

# Add the cron job
COPY cron_job /etc/cron.d/qbt_port_update
RUN chmod 0644 /etc/cron.d/qbt_port_update && \
    crontab /etc/cron.d/qbt_port_update

# Copy and make the entrypoint script executable
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Use entrypoint.sh as the entry point
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

