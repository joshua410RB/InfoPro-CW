import paho.mqtt.client as paho
import time 
import json
import threading
import logging
from database import *
from queue import Queue
import random

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

class Game:
    def __init__(self, ip, port):
        self.brokerip = ip
        self.brokerport = port
        self.bomb_server = paho.Client("BombHandler")
        self.game_server = paho.Client("GameHandler")
        self.rank_server = paho.Client("RankHandler")
        self.bomb_server.on_connect = self.on_connect_bomb
        self.bomb_server.on_publish = self.on_publish_bomb
        self.bomb_server.on_message = self.on_message_bomb
        self.game_server.on_connect = self.on_connect_game
        self.game_server.on_message = self.on_message_game
        self.rank_server.on_connect = self.on_connect_rank
        self.rank_server.on_publish = self.on_publish_rank
        self.username = "siyu"
        self.password = "password"

        # game data
        # global game started 
        self.started = False
        self.players = {}
        self.leaderboard = {}
        self.joining = Queue()
        self.bombcount = 0
        self.ready_data = {}

        # threads and starting processes
        self.mqtt_thread = threading.Thread(target=self.start_server_handler)
        self.join_thread = threading.Thread(target=self.handle_join)
        self.leaderboard_thread = threading.Thread(target=self.handle_leaderboard)
        self.bomb_thread = threading.Thread(target=self.handle_bomb)
        self.start_thread = threading.Thread(target=self.handle_start)

    def connect(self):
        try:
            self.bomb_server.username_pw_set(self.username, self.password)
            self.game_server.username_pw_set(self.username, self.password)
            self.rank_server.username_pw_set(self.username, self.password)
            self.bomb_server.connect(self.brokerip, self.brokerport)    
            self.game_server.connect(self.brokerip, self.brokerport)   
            self.rank_server.connect(self.brokerip, self.brokerport)   

        except:
            logging.debug("Connection Failed")
            exit(1)

    def threadstart(self):
        self.mqtt_thread.daemon = True
        self.join_thread.daemon = True
        self.bomb_thread.daemon = True
        self.leaderboard_thread.daemon  = True
        self.start_thread.daemon = True
        
        self.mqtt_thread.start()
        self.join_thread.start()
        self.bomb_thread.start()
        self.leaderboard_thread.start()
        self.start_thread.start()

    # MQTT Callbacks   
    # bomb 
    def on_connect_bomb(self, client, obj, flags, rc):
        if rc == 0:
            logging.debug("Bomb Control connected")
            client.subscribe("info/bomb", qos = 1)
        else:
            logging.debug("Bad connection")

    def on_publish_bomb(self, client, userdata, mid):
        pass
        # logging.debug("Publishing on Bomb Topic: " + str(mid))

    def on_message_bomb(self, client, userdata, msg):
        if str(msg.payload.decode("utf-8")) == "sendback":
            self.bombcount += 1
            logging.debug("got back bomb")

    # game: start, ready, end
    def on_connect_game(self, client, obj, flags, rc):
        if rc == 0:
            logging.debug("Game Control connected")
            client.subscribe("info/game", qos = 1)
        else:
            logging.debug("Bad connection")

    def on_message_game(self, client, userdata, msg):
        if str(msg.payload.decode("utf-8")) != "start":
            name, action = str(msg.payload.decode("utf-8")).split(":")
            if action == "join":
                if not self.started:
                    # if game started cannot join anymore
                    self.joining.put(name)
            elif action == "ready":
                logging.debug(name+" is ready")
                self.players[name].status = 1
            elif action == 'end':
                logging.debug(name+" ended")
                self.players[name].status = 2
                with players[name].speedq.mutex:
                    players[name].speedq.clear()

    # rank: leaderboards
    def on_connect_rank(self, client, obj, flags, rc):
        if rc == 0:
            logging.debug("Leaderboard Control started")
        else:
            logging.debug("Bad connection")

    def on_publish_rank(self, client, userdata, mid):
        pass
        # logging.debug("Publishing on Leaderboard Topic: " + str(mid))

    # Handlers
    def handle_join(self):
        while True:
            while not self.joining.empty():
                name = self.joining.get()
                if name in self.players:
                    continue
                self.players[name] = Player(self.brokerip, self.brokerport, name)

    def handle_start(self):
        while True:
            if self.started:
                time.sleep(0.01)
                # if all players end then game ends
                if all(player.status == 2 for (_, player) in self.players.items()):
                    self.started = False
                    logging.debug("game ended!")

                    # send last leaderboard to everyone
                    # reset everyone's status to not ready so we can play again
                    self.handle_leaderboard(True)
                    for _, player in self.players.items():
                        player.dist = 0
                        player.speed = 0
                        player.status = 0
            else:
                if len(self.players) == 0:
                    # cannot start if nobody join yet
                    continue
                
                # if all players are ready, start game
                if all(player.status == 1 for (_, player) in self.players.items()):
                    self.started = True
                    # send start to everyone
                    self.game_server.publish("info/game", "start", qos=1)
                    logging.debug("game started!!!!") 
                                 
                for name, player in self.players.items():
                    self.ready_data[name] = player.status
                    
                ready_json = json.dumps(self.ready_data)
                self.game_server.publish("info/game/ready", ready_json, qos=1)
                
                time.sleep(3) # have 5s for people to join before game auto starts


    def handle_bomb(self):
        while True:
            time.sleep(0.5)
            if self.bombcount == 0 and self.started:
                # send out a bomb!!! and rng who heheh
                self.bombcount -= 1
                name, _ = random.choice(list(self.players.items()))
                logging.debug("sent bomb to "+name)
                self.bomb_server.publish("info/bomb", name)

    def handle_leaderboard(self, last = False):
        while True:
            if(self.started or last):
                if last:
                    logging.debug("final leaderboard")
                    self.rank_server.publish("info/leaderboard/final", "final", qos=1)
                for name, player in self.players.items():
                    self.leaderboard[name] = int(player.dist)
                    sorted_tuples = sorted(self.leaderboard.items(), key=lambda item: item[1], reverse=True)
                    self.leaderboard = {k: v for k,v in sorted_tuples}
                    logging.debug(name+": "+str(self.leaderboard[name])+"m")
                    time.sleep(0.5)
                    leaderboard_data = json.dumps(self.leaderboard)
                    self.rank_server.publish("info/leaderboard", leaderboard_data, qos=1)

    def start_server_handler(self):
        logging.debug("Server Started")
        self.bomb_server.loop_start()
        self.rank_server.loop_start()
        self.game_server.loop_start()
        # bomb_event = 1
        while True:
            pass
        # while True:
        #     (rc, mid) = self.bomb_server.publish("info/bomb", str(bomb_event), qos=1)
        #     time.sleep(5)
        
class Player:
    def __init__(self, ip, port, playername):
        self.brokerip = ip
        self.brokerport = port
        self.playername = playername

        self.accel_server = paho.Client("AccelHandler_"+self.playername)
        self.accel_server.on_subscribe = self.on_subscribe_accel
        self.accel_server.on_message = self.on_message_accel
        self.accel_server.on_connect = self.on_connect_accel
        self.username = "siyu"
        self.password= "password"

        # player data
        self.dist = 0
        self.prev_speed = 0
        self.speed = 0
        self.speedq = Queue()
        self.status = 0 
        # 0 = not ready, 1 = ready, 2 = ended
        # think should add 2 = started and 3 = ended
        
        # threads and starting processes
        self.speedthread = threading.Thread(target=self.handle_speed)
        self.startthread = threading.Thread(target=self.start)
        self.connect()
        self.threadstart()
        
    def connect(self):
        try:
            self.accel_server.username_pw_set(self.username, self.password)
            self.accel_server.connect(self.brokerip, self.brokerport)
        except:
            logging.debug("Connection Failed")
            exit(1)
        
    def start(self):
        logging.debug(self.playername+" created")
        self.accel_server.loop_start()
        while True:
            pass
    
    def threadstart(self):
        self.speedthread.daemon = True
        self.startthread.daemon = True

        self.speedthread.start()
        self.startthread.start()

    # MQTT Callbacks    
    def on_subscribe_accel(self, client, userdata, mid, granted_qos):
        logging.debug("Accel Subscribed: "+self.playername+str(granted_qos))

    def on_message_accel(self, client, userdata, msg):
        # logging.debug(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))  
        speed = int(msg.payload.decode("utf-8"))
        if self.status == 1:
            self.speedq.put(speed)
        
    def on_connect_accel(self, client, obj, flags, rc):
        if rc == 0:
            logging.debug("Accel connected")
            client.subscribe("info/speed/"+self.playername, qos = 1)
        else:
            logging.debug("Bad connection")
    
    # Handlers 
    def handle_speed(self):
        while True:
            while not self.speedq.empty():
                if self.status is 0 or self.status is 2:
                    continue
                speed = self.speedq.get()
                self.calcDist(int(speed))

    # assumes linear acceleration between speed datas
    def calcDist(self, newspeed):
        self.prev_speed = self.speed 
        self.speed = newspeed
        self.dist += 1/2*(self.speed + self.prev_speed)*0.1 # timestep

def main():
    game = Game("localhost", 1883)
    game.connect()
    game.threadstart()

    while True:
        pass

if __name__ == "__main__":
    main()