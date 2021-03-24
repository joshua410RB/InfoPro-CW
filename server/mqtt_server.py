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
        self.final_leaderboard = threading.Event()
        self.final_leaderboard.clear()
        self.players = {}
        self.leaderboard = {}
        self.bombs = Queue() # list of names where the bomb comes from
        self.joining = Queue()
        self.ready_data = {}
        self.dead_people = {}

        # db stuff
        self.db = create_connection('db/racegame.db')

        # threads and starting processes
        self.mqtt_thread = threading.Thread(target=self.start_server_handlerl, daemon=True)
        self.join_thread = threading.Thread(target=self.handle_join, daemon=True)
        self.leaderboard_thread = threading.Thread(target=self.handle_leaderboard, daemon=True)
        self.bomb_thread = threading.Thread(target=self.handle_bomb, daemon=True)
        self.start_thread = threading.Thread(target=self.handle_start, daemon=True)

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
        name, action = str(msg.payload.decode("utf-8")).split(":")
        if action == "sendbomb":
            logging.debug(name+" wants to bomb")
            self.bombs.put(name)

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
                try:
                    logging.debug(name+" is ready")
                    self.players[name].status = 1
                except:
                    logging.debug(name+" hasn't joined yet, please join first!")
            elif action == 'end':
                logging.debug(name+" ended race")
                self.players[name].status = 2
            elif action == 'died':
                logging.debug(name+" died")
                self.handle_disconnect(name)

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
                    break
                try:
                    # if player exist but dead
                    player = self.dead_people[name]
                    self.players[name] = player
                    del self.dead_people[name]
                except:
                    self.players[name] = Player(self.brokerip, self.brokerport, name)

    def handle_start(self):
        while True:
            if self.started:
                time.sleep(0.1)
                # if all players end then game ends
                if all(player.status == 2 for (_, player) in self.players.items()):
                    self.started = False
                    logging.debug("game ended!")

                    # send last leaderboard to everyone
                    self.final_leaderboard.set()

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
            time.sleep(0.1)
            if self.started and not self.bombs.empty():
                sender = self.bombs.get()
                sendee = sender
                randomise = False
                # trying to send to the person ahead of you
                # if first place then random send
                leaderboard_dict = self.leaderboard.copy()
                for i, name in enumerate(leaderboard_dict):                    
                    if name == sender and i != 0:
                        break
                    elif name == sender and i == 0:
                        randomise = True
                        break
                    sendee = name

                if randomise:
                    sendee, _ = random.choice(list(self.players.items()))

                logging.debug("sent bomb to "+sendee)
                self.bomb_server.publish("info/bomb", sendee+":bomb")

    def handle_leaderboard(self):
        while True:
            if(self.started or self.final_leaderboard.is_set()):
                time.sleep(0.1)
                players_dict = self.players.copy()
                for name, player in players_dict.items():
                    self.leaderboard[name] = int(player.dist)
                    sorted_tuples = sorted(self.leaderboard.items(), key=lambda item: item[1], reverse=True)
                    self.leaderboard = {k: v for k,v in sorted_tuples}
                    logging.debug(name+": "+str(self.leaderboard[name])+"m")
                    # sort by position
                    leaderboard_data = json.dumps(self.leaderboard)
                    self.rank_server.publish("info/leaderboard", leaderboard_data, qos=1)
                if self.final_leaderboard.is_set():
                    logging.debug("final leaderboard")
                    # add to sql database and get alltime highscore
                    self.add_to_db()
                    highscore_dict = self.get_highscore()
                    self.rank_server.publish("info/leaderboard/final", "final", qos=1)
                    highscore_json = json.dumps(highscore_dict)
                    self.rank_server.publish("info/leaderboard/highscore", highscore_json, qos=1)
                    self.final_leaderboard.clear()  
                    for _, player in players_dict.items():
                        player.dist = 0
                        player.status = 0
                    logging.debug("Game Data Erased")

    def handle_disconnect(self, name):
        try:
            logging.debug("moving to dead people list")
            self.players[name].disconnect = True
            time.sleep(0.1)
            # self.players[name].speedthread.join()
            self.players[name].startthread.join()
            player = self.players[name]
            self.dead_people[name] = player
            del self.players[name]
            del self.ready_data[name]
            del self.leaderboard[name]
            logging.debug("deleted all instances of "+name)
        except:
            logging.debug("deleted all instances of "+name)

    def start_server_handler(self):
        logging.debug("Server Started")
        self.bomb_server.loop_start()
        self.rank_server.loop_start()
        self.game_server.loop_start()
        while True:
            pass

    def add_to_db(self):
        # create game record assume leaderboard sorted alr
        leaderboard_copy = self.leaderboard.copy()
        res = []
        for name, _ in leaderboard_copy:
            res.append(name)

        while(len(res) < 6):
            res.append(None)

        gameid = create_game_record(self.db, res)
        # create dist record
        for name, dist in leaderboard_copy:
            create_distance_record(self.db, (name, int(dist), gameid))

    def get_highscore(self):
        # highscore is a list of lists
        highscore = select_highscore(self.db)
        highscore_dict = { i: (item[0], item[1]) for i, item in enumerate(highscore)}
        return highscore_dict

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

        ## player data for current game 
        self.dist = 0
        self.status = 0 
        # 0 = not ready, 1 = ready, 2 = ended
        self.disconnect = False
        
        # threads and starting processes
        # self.speedthread = threading.Thread(target=self.handle_speed, daemon=True)
        self.startthread = threading.Thread(target=self.start, daemon=True)
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
            time.sleep(0.5)
            if(self.disconnect):
                break
        
        logging.debug("start thread ended")
    
    def threadstart(self):
        # self.speedthread.start()
        self.startthread.start()

    # MQTT Callbacks    
    def on_subscribe_accel(self, client, userdata, mid, granted_qos):
        logging.debug("Accel Subscribed: "+self.playername+str(granted_qos))

    def on_message_accel(self, client, userdata, msg):
        # logging.debug(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))  
        dist = int(msg.payload.decode("utf-8"))
        if self.status == 1:
            self.dist = dist
        
    def on_connect_accel(self, client, obj, flags, rc):
        if rc == 0:
            logging.debug("Accel connected")
            client.subscribe("info/dist/"+self.playername, qos = 1)
        else:
            logging.debug("Bad connection")
    
    # # Handlers 
    # def handle_dist(self):
    #     while True:
    #         while not self.distq.empty():
    #             if self.status == 0 or self.status == 2:
    #                 continue
    #             dist = self.distq.get()
    #             # self.calcDist(int(speed))
            
    #         if(self.disconnect):
    #             break
        
    #     logging.debug("speed thread ended")

    # # assumes linear acceleration between speed datas
    # def calcDist(self, newspeed):
    #     self.prev_speed = self.speed 
    #     self.speed = newspeed
    #     self.dist += 1/2*(self.speed + self.prev_speed)*0.1 # timestep

def main():
    game = Game("0.0.0.0", 1883)
    game.connect()
    game.threadstart()

    while True:
        pass

if __name__ == "__main__":
    main()