import paho.mqtt.client as paho
import time
import threading,queue
import logging
from random import randint

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )
test_data = queue.Queue()

def on_publish(client, userdata, mid):
    # print("mid: "+str(mid))
    pass

def on_connect_accel(client, obj, flags, rc):
    if rc == 0:
        logging.debug("Accel connected")
    else:
        logging.debug("Bad connection")

def on_connect_bomb(client, obj, flags, rc):
    if rc == 0:
        logging.debug("Bomb connected")
        client.subscribe("info/bomb", qos = 1)
    else:
        logging.debug("Bad connection")


def on_message(client, obj, msg):
    logging.debug(msg.topic + " " + str(msg.payload))

def begin_mqtt_client():
    accel_client = paho.Client("node1")
    bomb_client = paho.Client("node2")
    accel_client.on_connect = on_connect_accel
    bomb_client.on_connect = on_connect_bomb
    accel_client.on_publish = on_publish
    bomb_client.on_message = on_message

    accel_client.connect("localhost", 1883)
    bomb_client.connect("localhost", 1883)

    accel_client.loop_start()
    bomb_client.loop_start()
    while True:
        sensor_data = test_data.get()
        (rc, mid) = accel_client.publish("info/accel", "Device2:"+str(sensor_data), qos=1)
        time.sleep(0.5)
        logging.debug(sensor_data)

def generate_random():
    logging.debug("Starting Generation")
    index = 0
    while True:
        test_data.put(randint(0,10))
        time.sleep(0.5)
        # if (index == 1000):
        #     break
        index += 1
    logging.debug("Exiting Generation")


def main():
    x = threading.Thread(target=generate_random)
    y = threading.Thread(target=begin_mqtt_client)
    x.start()
    y.start()

if __name__ == "__main__":
    main()