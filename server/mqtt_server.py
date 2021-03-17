import paho.mqtt.client as paho
import time 
import logging
from database import *

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
        client.subscribe("info/speed", qos = 1)
    else:
        print("Bad connection")

def on_connect_game(client, obj, flags, rc):
    if rc == 0:
        print("Game Control connected")
        client.subscribe("info/game", qos = 1)
    else:
        print("Bad connection")

def on_message_game(client, userdata, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))  

class mqtt_server_handler:
    def __init__(self, ip, port):
        self.brokerip = ip
        self.brokerport = port
        self.accel_server = paho.Client("AccelHandler")
        self.bomb_server = paho.Client("BombHandler")
        self.game_server = paho.Client("GameHandler")
        self.accel_server.on_subscribe = on_subscribe
        self.accel_server.on_message = on_message
        self.accel_server.on_connect = on_connect_accel
        self.bomb_server.on_publish = on_publish
        self.username = "siyu"
        self.password = "password"


    def connect(self):
        try:
            self.accel_server.username_pw_set(self.username, self.password)
            self.bomb_server.username_pw_set(self.username, self.password)
            self.accel_server.connect(self.brokerip, self.brokerport)
            self.bomb_server.connect(self.brokerip, self.brokerport)        

        except:
            logging.debug("Connection Failed")
            exit(1)

    def start_server_handler(self):
        logging.debug("Server Started")
        self.bomb_server.loop_start()
        self.accel_server.loop_start()
        bomb_event = 1
        while True:
            (rc, mid) = self.bomb_server.publish("info/bomb", str(bomb_event), qos=1)
            time.sleep(5)

def main():
    mqtt = mqtt_server_handler("localhost", 1883)
    mqtt.connect()
    mqtt.start_server_handler()

if __name__ == "__main__":
    main()