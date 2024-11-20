#!/bin/bash

# Set default values for HOST_UID and HOST_GID if not set
: ${PUID:=1000}
: ${PGID:=1000}

# Ensure /config and its contents are owned by the specified UID and GID
chown -R $PUID:$PGID /config

# Ensure the cron job has correct permissions and ownership
chmod 0644 /etc/cron.d/qbt_port_update

# Replace the entire cron line with the new cron schedule and user (appuser)
sed -i "s|^.*/venv|$CRON_SCHEDULE   /venv|" /etc/cron.d/qbt_port_update

# Write environment variables to a file
printenv | grep -E "GLUETUN|QBITTORRENT|QBT|LOG|CRON" | sort > /etc/environment

# Ensure cron jobs can see the environment
chmod 0644 /etc/environment

# Apply the cron job as root
crontab /etc/cron.d/qbt_port_update

# Start the cron daemon in the background
cron

# Run the Python script immediately
echo "---------------------------------------------------------------------------------------------------"
/venv/bin/python /usr/local/bin/qbt_port_update.py -v
cat /etc/environment
echo "---------------------------------------------------------------------------------------------------"
/venv/bin/python /usr/local/bin/qbt_port_update.py >> /proc/1/fd/1 2>> /proc/1/fd/2

# Keep the container running by tailing /dev/null
exec tail -f /dev/null
