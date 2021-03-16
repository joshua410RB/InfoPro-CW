#!/bin/bash

#Start MQTT Broker
mosquitto -d

#Run mqtt server script
python3 mqtt_server.py &
#Run flask server for dashboard
python3 mqtt_flask.py 