import argparse
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


final_results = {}

class mqtt_client_test:
    def __init__(self, ip, port, username, encrypt, final_dist, send_bomb):
        self.brokerip = ip
        self.brokerport = port
        self.playername = username
        self.accel_client = paho.Client("accel_"+self.playername)
        self.bomb_client = paho.Client("bomb_"+self.playername)
        self.game_client = paho.Client("game_"+self.playername)
        self.rank_client = paho.Client("rank_"+self.playername)
        self.accel_client.on_connect = self.on_connect_accel
        self.bomb_client.on_connect = self.on_connect_bomb
        self.bomb_client.on_message = self.on_message_bomb
        self.game_client.on_connect = self.on_connect_game
        self.game_client.on_subscribe = self.on_sub_game
        self.game_client.on_message = self.on_message_game
        self.game_client.on_publish = self.on_publish_game
        self.rank_client.on_connect = self.on_connect_rank
        self.rank_client.on_message = self.on_message_rank
        self.rank_client.on_subscribe =self.on_sub_rank
        self.encrypt = encrypt
        self.ready_flag = config.ready_flag
        # self.start_flag = config.start_flag
        self.end_flag = config.end_flag
        self.final_flag = config.final_flag
        self.send_bomb_flag = config.send_bomb_flag
        self.bombed_flag = config.bombed_flag
        self.ready = config.ready_object
        self.final_dist = final_dist
        self.send_bomb = send_bomb
        
        # game details
        self.started = False
        self.leaderboard = config.leaderboard_object
        self.highscore = config.highscore_object
        
    def connect(self):
        try:           
            if self.encrypt:
                self.accel_client.tls_set('assets/ca.crt')
                self.bomb_client.tls_set('assets/ca.crt')
                self.game_client.tls_set('assets/ca.crt')
                self.rank_client.tls_set('assets/ca.crt')
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
            logging.debug("Simulated Client Connected")
        except:
            logging.debug("Connection to {} via port {} has failed ".format(self.brokerip, self.brokerport))
            exit(1)

    def start_client(self):
        logging.debug("Client Started")
        print("Hello")
        # self.start_flag.clear()
        self.final_flag.clear()
        self.bomb_client.loop_start()
        self.accel_client.loop_start()
        self.game_client.loop_start()
        self.rank_client.loop_start()
        send_count = 0

        while send_count < 3:
            logging.debug("Sending Ready")
            self.game_client.publish("info/game", self.playername+":ready", qos=1)
            logging.debug(self.playername+" is ready")
            send_count += 1

        time.sleep(0.1) 
        if self.send_bomb:
            dist = 0
        else:
            dist = 200
        while not self.started:
            pass

        if self.started:
            # start sending speed data
            logging.debug("Sending Game Distance Data")
            while dist <= self.final_dist:
                self.accel_client.publish("info/dist/"+self.playername, dist, qos=1)
                time.sleep(0.1)
                dist += 100
                if self.send_bomb and dist == 1000:
                    logging.debug("throw bomb")
                    self.bomb_client.publish("info/bomb", self.playername+":sendbomb", qos=1)
                    config.bomb_sent = time.time()

        logging.debug(self.playername+" finished")
        time.sleep(1)
        self.game_client.publish("info/game", self.playername+":end", qos=1)

        # if self.send_bomb_flag.is_set():
        #     # send bomb
        #     logging.debug("throw bomb")
        #     self.send_bomb_flag.clear()
        #     self.bomb_client.publish("info/bomb", self.playername+":sendbomb", qos=1)


    # MQTT callbacks
    # speed 

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
        logging.debug(str(msg.payload.decode("utf-8")))
        involved, action = str(msg.payload.decode("utf-8")).split(":")
        if action == 'bomb':
            name, sender = involved.split("-")
            if name == self.playername:
                # received bomb
                config.bomb_sender = sender
                logging.debug(msg.topic + " bombed by " +sender+":(")
                self.bombed_flag.set()
                config.bomb_received = time.time()
    
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
            pass
            # # json of ready data
            # data = str(msg.payload.decode("utf-8", "ignore"))
            # logging.debug("client ready data: "+data)
            # data = json.loads(data) # decode json data
            # self.ready.update(data)
        else:
            if message == "start":
                logging.debug("game started")
                # self.start_flag.set()
                self.started = True

    # leaderboards
    def on_sub_rank(self, client, userdata, mid, granted_qos):
        logging.debug("Subscribed: Leaderboard "+str(mid)+" "+str(granted_qos))

    def on_connect_rank(self, client, obj, flags, rc):
        if rc == 0:
            logging.debug("Rank connected!")
            client.subscribe("info/leaderboard", qos = 1)
            client.subscribe("info/leaderboard/final", qos = 1)
            client.subscribe("info/leaderboard/highscore", qos = 1)
        else:
            logging.debug("Bad connection", )

    def on_message_rank(self, client, obj, msg):
        if msg.topic == "info/leaderboard/final":
            self.final_flag.set()
        elif msg.topic == "info/leaderboard/highscore":
            data = str(msg.payload.decode("utf-8", "ignore"))
            logging.debug("client highscores: "+data)
            data = json.loads(data) # decode json data
            self.highscore.update(data)
        else:
            data = str(msg.payload.decode("utf-8", "ignore"))
            # logging.debug("client leaderboard: "+data)
            data = json.loads(data) # decode json data
            # sort by position
            sorted_tuples = sorted(data.items(), key=lambda item: item[1], reverse=True)
            sorted_dict = {}
            for i in range(len(sorted_tuples)):
                sorted_dict[i] = sorted_tuples[i]
            self.leaderboard.update(sorted_dict)

        # add final leaderboard to a global dictionary for checking
        if self.final_flag.is_set():
            final_results[self.playername] = self.leaderboard
            logging.debug("Adding to final result")

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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Racing Game')
    parser.add_argument('--serverip', 
                        default="localhost",
                        help='input your server ip')
    parser.add_argument('--port', 
                        default= 1883,
                        help='input your server port')
    parser.add_argument('-e', '--encrypt', action='store_true',
                        help='Use encryption using TLS')
    parser.add_argument('-w', '--wsl', action='store_true',
                        help='Playing on WSL')


    args = parser.parse_args()
    dist = 3000
    
    mqtt = mqtt_client_test(args.serverip, int(args.port), "bomb_sender", args.encrypt, dist, True)
    mqtt.connect()
    bomb_sender = threading.Thread(target=mqtt.start_client, daemon=True)
    
    mqtt2 = mqtt_client_test(args.serverip, int(args.port), "bomb_receiver", args.encrypt, dist, False)
    mqtt2.connect()
    bomb_receiver = threading.Thread(target=mqtt2.start_client, daemon=True)

    logging.debug("Starting")
    
    
    bomb_receiver.start()
    bomb_sender.start()
        
    while config.bomb_received == 0 or config.bomb_sent == 0: 
        print(config.bomb_received, config.bomb_sent)
        pass

    print("Bomb Feature Simulation Passed and took {}s !".format(config.bomb_received - config.bomb_sent))
    