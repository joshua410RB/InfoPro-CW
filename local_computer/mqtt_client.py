import paho.mqtt.client as paho
import time
import threading,queue
import logging
from random import randint
import subprocess
import json
import ssl
import config

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

# ----------------MQTT Settings-----------------

class mqtt_client:
    def __init__(self, ip, port, username, password, encrypt, 
                 accel_data, ready_flag, start_flag, final_flag, 
                 leaderboard_object, ready_object, end_flag, send_bomb_flag, bombed_flag):
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
        self.username = username
        self.password = password
        self.encrypt = encrypt
        self.accel_data = accel_data
        self.ready_flag = ready_flag
        self.start_flag = start_flag
        self.end_flag = end_flag
        self.final_flag = final_flag
        self.send_bomb_flag = send_bomb_flag
        self.bombed_flag = bombed_flag
        self.ready = ready_object

        # game details
        self.started = False
        self.leaderboard = leaderboard_object
        
    def connect(self):
        try:            
            # self.accel_client.username_pw_set(self.username, self.password)
            # self.bomb_client.username_pw_set(self.username, self.password)
            if self.encrypt:
                self.accel_client.tls_set('/mnt/c/Users/tansi/Documents/Imperial_College_London/Info_Processing/InfoPro-CW/local_computer/ca.crt')
                self.bomb_client.tls_set('/mnt/c/Users/tansi/Documents/Imperial_College_London/Info_Processing/InfoPro-CW/local_computer/ca.crt')
                self.game_client.tls_set('/mnt/c/Users/tansi/Documents/Imperial_College_London/Info_Processing/InfoPro-CW/local_computer/ca.crt')
                self.rank_client.tls_set('/mnt/c/Users/tansi/Documents/Imperial_College_London/Info_Processing/InfoPro-CW/local_computer/ca.crt')
                self.accel_client.tls_insecure_set(True)
                self.bomb_client.tls_insecure_set(True)
                self.game_client.tls_insecure_set(True)
                self.rank_client.tls_insecure_set(True)

            lwm = self.playername+":died"
            self.game_client.will_set("info/game", lwm, qos=1, retain=False)
            self.accel_client.connect(self.brokerip, self.brokerport)
            self.bomb_client.connect(self.brokerip, self.brokerport)        
            self.game_client.connect(self.brokerip, self.brokerport)
            self.rank_client.connect(self.brokerip, self.brokerport)
        except:
            logging.debug("Connection to {} via port {} has failed ".format(self.brokerip, self.brokerport))
            exit(1)

    def start_client(self):
        logging.debug("Client Started")
        self.start_flag.clear()
        self.final_flag.clear()
        self.bomb_client.loop_start()
        self.accel_client.loop_start()
        self.game_client.loop_start()
        self.rank_client.loop_start()
        time.sleep(2)
        send_count = 0
        while True:
            time.sleep(0.1)
            if self.started:
                time.sleep(0.5)
                # start sending speed data
                try:
                    # sensor_data = self.accel_data.popleft()
                    # logging.debug("Speed: "+str(sensor_data))
                    logging.debug("Dist: "+str(config.dist_data))
                    self.accel_client.publish("info/dist/"+self.playername, config.dist_data, qos=1)
                except IndexError:
                    logging.debug("accel_data empty queue")

                if self.end_flag.is_set():
                    # if game ended
                    self.started = False
                    logging.debug(self.playername+" finished")
                    self.game_client.publish("info/game", self.playername+":end", qos=1)

                if self.send_bomb_flag.is_set():
                    # send bomb
                    logging.debug("throw bomb")
                    self.send_bomb_flag.clear()
                    self.bomb_client.publish("info/bomb", self.playername+":sendbomb", qos=1)
            else:
                # refresh to check if ready every 2s
                if (self.ready_flag.is_set() and send_count<3):
                    logging.debug(self.playername+" is ready")
                    self.game_client.publish("info/game", self.playername+":ready", qos=1)
                    send_count+= 1
                if send_count == 3:
                    self.ready_flag.clear()
                    send_count=0

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
        name, action = str(msg.payload.decode("utf-8")).split(":")
        if action == 'bomb' and name == self.playername:
            # received bomb
            logging.debug(msg.topic + " bombed :(")
            self.bombed_flag.set()
    
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
            client.subscribe("info/game/ready", qos = 1)
            logging.debug("joined game")
            client.publish("info/game", self.playername+":join", qos = 1)
        else:
            logging.debug("Bad connection", )

    def on_message_game(self, client, obj, msg):
        message = str(msg.payload.decode("utf-8"))
        if msg.topic == 'info/game/ready':
            # json of ready data
            data = str(msg.payload.decode("utf-8", "ignore"))
            logging.debug("client ready data: "+data)
            data = json.loads(data) # decode json data
            self.ready.update(data)
        else:
            if message == "start":
                logging.debug("game started")
                self.start_flag.set()
                self.started = True

    # leaderboards
    def on_sub_rank(self, client, userdata, mid, granted_qos):
        logging.debug("Subscribed: Leaderboard "+str(mid)+" "+str(granted_qos))

    def on_connect_rank(self, client, obj, flags, rc):
        if rc == 0:
            logging.debug("Rank connected!")
            client.subscribe("info/leaderboard", qos = 1)
            client.subscribe("info/leaderboard/final", qos = 1)
        else:
            logging.debug("Bad connection", )

    def on_message_rank(self, client, obj, msg):
        if msg.topic == "info/leaderboard/final":
            self.final_flag.set()
        else:
            data = str(msg.payload.decode("utf-8", "ignore"))
            # logging.debug("client leaderboard: "+data)
            data = json.loads(data) # decode json data
            # sort by position
            sorted_tuples = sorted(data.items(), key=lambda item: item[1], reverse=True)
            sorted_dict = {k: v for k,v in sorted_tuples}
            self.leaderboard.update(sorted_dict)

    # handlers
    def show_leaderboard(self):
        logging.debug("Printing leaderboard")
        while True:
            pass
            # for name, dist in self.leaderboard.items():
            #     logging.debug(name+": "+str(dist))

    def handle_bomb(self):
        while True:
            if self.send_bomb_flag.is_set():
                # send bomb
                logging.debug("throw bomb")
                time.sleep(5)
                self.send_bomb_flag.clear()
                self.bomb_client.publish("info/bomb", self.playername+":sendbomb", qos=1)

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
    x = threading.Thread(target=generate_random, daemon=True)
    # x = threading.Thread(target=receive_val, args={'o'})
    y = threading.Thread(target=mqtt.start_client, daemon=True)
    rank = threading.Thread(target=mqtt.show_leaderboard, daemon=True)
    bomb = threading.Thread(target=mqtt.handle_bomb, daemon=True)
    x.start()
    y.start()
    rank.start()
    bomb.start()

if __name__ == "__main__":
    main()