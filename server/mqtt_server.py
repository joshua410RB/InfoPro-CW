import paho.mqtt.client as paho
import time 
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))    

def on_publish(client, userdata, mid):
    print("Publishing on Bomb Topic: " + str(mid))

def on_connect_accel(client, obj, flags, rc):
    if rc == 0:
        print("Accel connected")
        client.subscribe("info/accel", qos = 1)
    else:
        print("Bad connection")

accel_server = paho.Client("AccelHandler")
bomb_server = paho.Client("BombHandler")
accel_server.on_subscribe = on_subscribe
accel_server.on_message = on_message
accel_server.on_connect = on_connect_accel
bomb_server.on_publish = on_publish

accel_server.connect("localhost", 1883)
bomb_server.connect("localhost", 1883)


bomb_server.loop_start()
accel_server.loop_start()

bomb_event = 1
while True:
    (rc, mid) = bomb_server.publish("info/bomb", str(bomb_event), qos=1)
    time.sleep(5)
