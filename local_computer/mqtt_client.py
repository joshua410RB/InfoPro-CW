import paho.mqtt.client as paho
import time
import threading,queue
import logging
from random import randint
import subprocess
import json

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )
speed_data = queue.Queue()
current_mode = threading.Event()
mode_change = threading.Condition()

# ----------------MQTT Settings-----------------

class mqtt_client:
    def __init__(self, ip, port, username, accel_data):
        self.brokerip = ip
        self.brokerport = port
        self.playername = username
        self.accel_client = paho.Client("accel_"+self.playername)
        self.bomb_client = paho.Client("bomb_"+self.playername)
        self.game_client = paho.Client("game_"+self.playername)
        self.rank_client = paho.Client("rank_"+self.playername)
        self.accel_client.on_connect = self.on_connect_accel
        self.accel_client.on_publish = self.on_publish_accel
        self.bomb_client.on_connect = self.on_connect_bomb
        self.bomb_client.on_message = self.on_message_bomb
        self.game_client.on_connect = self.on_connect_game
        self.game_client.on_subscribe = self.on_sub_game
        self.game_client.on_message = self.on_message_game
        self.game_client.on_publish = self.on_publish_game
        self.rank_client.on_connect = self.on_connect_rank
        self.rank_client.on_message = self.on_message_rank
        self.rank_client.on_subscribe =self.on_sub_rank
        # self.username = "siyu"
        # self.password = "password"
        self.accel_data = accel_data

        # game details
        self.started = False
        self.bombed = False
        self.leaderboard = {}

    def connect(self):
        try:            
            # self.accel_client.username_pw_set(self.username, self.password)
            # self.bomb_client.username_pw_set(self.username, self.password)
            # self.accel_client.tls_set('/mnt/c/Users/tansi/Documents/Imperial_College_London/Info_Processing/InfoPro-CW/local_computer/ca.crt')
            # self.bomb_client.tls_set('/mnt/c/Users/tansi/Documents/Imperial_College_London/Info_Processing/InfoPro-CW/local_computer/ca.crt')
            # self.accel_client.tls_insecure_set(True)
            # self.bomb_client.tls_insecure_set(True)
            self.accel_client.connect(self.brokerip, self.brokerport)
            self.bomb_client.connect(self.brokerip, self.brokerport)        
            self.game_client.connect(self.brokerip, self.brokerport)
            self.rank_client.connect(self.brokerip, self.brokerport)
        except:
            logging.debug("Connection Failed")
            exit(1)

    def start_client(self):
        logging.debug("Client Started")
        self.bomb_client.loop_start()
        self.accel_client.loop_start()
        self.game_client.loop_start()
        self.rank_client.loop_start()
        time.sleep(2)
        while True:
            if self.started:
                # start sending speed data
                if not self.accel_data.empty():
                    sensor_data = self.accel_data.get()
                    if self.bombed:
                        sensor_data = int(sensor_data/2)
                    logging.debug("Speed: "+str(sensor_data))
                    self.accel_client.publish("info/speed/"+self.playername, str(sensor_data), qos=1)
                # else:
                #     # game end
                #     self.started = False
                #     logging.debug(self.playername+" finished")
                #     self.game_client.publish("info/game", self.playername+":end", qos=1)
            else:
                # 10s to get ready
                time.sleep(10)
                logging.debug(self.playername+" is ready")
                self.game_client.publish("info/game", self.playername+":ready", qos=1)

    # MQTT callbacks
    # speed 
    def on_publish_accel(self, client, userdata, mid):
        pass
        # logging.debug("publishing message no.: "+str(mid))

    def on_connect_accel(self, client, obj, flags, rc):
        if rc == 0:
            logging.debug("Accel connected")
        else:
            logging.debug("Bad connection")

    # bomb
    def on_connect_bomb(self, client, obj, flags, rc):
        if rc == 0:
            logging.debug("Bomb connected")
            client.subscribe("info/bomb", qos = 1)
        else:
            logging.debug("Bad connection")

    def on_message_bomb(self, client, obj, msg):
        message = str(msg.payload.decode("utf-8"))
        if message == self.playername:
            # received bomb
            self.bombed = True
            logging.debug(msg.topic + " received bomb")
    
    # game settings
    def on_publish_game(self, client, userdata, mid):
        pass
        # logging.debug("Publishing on Game Topic: " + str(mid))

    def on_sub_game(self, client, userdata, mid, granted_qos):
        logging.debug("Subscribed: Game "+str(mid)+" "+str(granted_qos))

    def on_connect_game(self, client, obj, flags, rc):
        if rc == 0:
            logging.debug("Game connected!")
            client.subscribe("info/game", qos = 1)
            logging.debug("joined game")
            client.publish("info/game", self.playername+":join", qos = 1)
        else:
            logging.debug("Bad connection", )

    def on_message_game(self, client, obj, msg):
        message = str(msg.payload.decode("utf-8"))
        if message == "start":
            logging.debug("game started")
            self.started = True
            # start local timer?

    # leaderboards
    def on_sub_rank(self, client, userdata, mid, granted_qos):
        logging.debug("Subscribed: Leaderboard "+str(mid)+" "+str(granted_qos))

    def on_connect_rank(self, client, obj, flags, rc):
        if rc == 0:
            logging.debug("Rank connected!")
            client.subscribe("info/leaderboard", qos = 1)
        else:
            logging.debug("Bad connection", )

    def on_message_rank(self, client, obj, msg):
        time.sleep(1)
        data = str(msg.payload.decode("utf-8", "ignore"))
        logging.debug("leaderboard: "+data)
        data = json.loads(data) # decode json data
        self.leaderboard = data

    # handlers
    def show_leaderboard(self):
        logging.debug("Printing leaderboard")
        while True:
            time.sleep(1)
            # for name, dist in self.leaderboard.items():
            #     logging.debug(name+": "+str(dist))

    def handle_bomb(self):
        while True:
            time.sleep(0.1)
            if self.bombed:
                # must hold for at least 2s 
                time.sleep(2)
                # send bomb
                self.bombed = False
                logging.debug("throw back bomb")
                self.bomb_client.publish("info/bomb", "sendback", qos=1)

# ----------------UART Data-----------------
def generate_random():
    logging.debug("Starting Generation")
    index = 0
    while True:
        speed_data.put(randint(0,10))
        time.sleep(0.5)
        index += 1
    logging.debug("Exiting Generation")


def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is


def main():
    # mqtt = mqtt_client("13.212.218.108", 8883)
    mqtt = mqtt_client("localhost", 1883, "siting")
    mqtt.connect()
    x = threading.Thread(target=generate_random)
    # x = threading.Thread(target=receive_val, args={'o'})
    y = threading.Thread(target=mqtt.start_client)
    rank = threading.Thread(target=mqtt.show_leaderboard)
    bomb = threading.Thread(target=mqtt.handle_bomb)
    x.start()
    y.start()
    rank.start()
    bomb.start()

if __name__ == "__main__":
    main()