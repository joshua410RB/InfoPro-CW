#!/bin/sh

if [[ ! -f db/racegame.db ]]; then
    echo "Creating database file"
    python3 database.py
fi

mosquitto -d -c /etc/mosquitto/mosquitto.conf
python3 mqtt_server.py

