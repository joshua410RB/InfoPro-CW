#!/bin/sh

mosquitto -d -c /etc/mosquitto/mosquitto.conf
python3 mqtt_server.py

