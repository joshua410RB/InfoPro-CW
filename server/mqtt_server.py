import paho.mqtt.client as paho
import time 
import threading
import logging
from database import *
from queue import Queue

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

class Game:
    def __init__(self, ip, port):
        self.brokerip = ip
        self.brokerport = port
        self.bomb_server = paho.Client("BombHandler")
        self.game_server = paho.Client("GameHandler")
        self.bomb_server.on_connect = self.on_connect_bomb
        self.bomb_server.on_publish = self.on_publish_bomb
        self.game_server.on_connect = self.on_connect_game
        self.game_server.on_message = self.on_message_game
        self.username = "siyu"
        self.password = "password"

        # game data
        self.started = False
        self.people = {}
        self.leaderboard = []
        self.joining = Queue()
        self.bombs = Queue()

        # threads and starting processes
        self.mqtt_thread = threading.Thread(target=self.start_server_handler)
        self.join_thread = threading.Thread(target=self.handle_join)
        self.leaderboard_thread = threading.Thread(target=self.handle_leaderboard)
        self.bomb_thread = threading.Thread(target=self.handle_bomb)
        self.connect()
        self.threadstart()

    def connect(self):
        try:
            self.bomb_server.username_pw_set(self.username, self.password)
            self.game_server.username_pw_set(self.username, self.password)
            self.bomb_server.connect(self.brokerip, self.brokerport)    
            self.game_server.connect(self.brokerip, self.brokerport)      

        except:
            logging.debug("Connection Failed")
            exit(1)

    def threadstart(self):
        self.mqtt_thread.start()
        self.join_thread.start()
        self.bomb_thread.start()
        self.leaderboard_thread.start()

    # MQTT Callbacks    
    def on_connect_bomb(self, client, obj, flags, rc):
        if rc == 0:
            logging.debug("Bomb Control connected")
            client.subscribe("info/bomb", qos = 1)
        else:
            logging.debug("Bad connection")

    def on_publish_bomb(self, client, userdata, mid):
        logging.debug("Publishing on Bomb Topic: " + str(mid))

    def on_connect_game(self, client, obj, flags, rc):
        if rc == 0:
            logging.debug("Game Control connected")
            client.subscribe("info/game", qos = 1)
        else:
            logging.debug("Bad connection")

    def on_message_game(self, client, userdata, msg):        
        name, action = str(msg.payload.decode("utf-8")).split(":")
        if action == "join":
        # decode name to string
            self.joining.put(name)
            logging.debug(str(msg.topic)+" "+str(name)+" joined")
    
    # Handlers
    def handle_join(self):
        while True:
            while not self.joining.empty():
                name = self.joining.get()
                if name in self.people:
                    continue
                logging.debug("Created "+name+" player")
                self.people[name] = Player(self.brokerip, self.brokerport, name)

    def handle_gameend(self):
        pass

    def handle_bomb(self):
        while True:
            pass
            # if self.bombcount is 0:
            #     # end out a bomb!!! and choose who
            #     self.bombcount = 1
            #     name = "Device1"
            #     self.mqtt.bomb_server.publish("info/bomb", name)
            # while not self.bombs.empty():
            #     logging.debug("sendingbomb")
            #     name = self.bombs.get().split(":")

    def handle_leaderboard(self):
        while True:
            # if not self.started:
            #     self.started = True
            
            # if(self.started):
            # TODO : Publish to leaderboard as JSON and convert to int
            for _, player in self.people.items():
                logging.debug(player.playername+": "+str(player.dist))

            time.sleep(1)
    
    def start_server_handler(self):
        logging.debug("Server Started")
        self.bomb_server.loop_start()
        self.game_server.loop_start()
        # bomb_event = 1
        while True:
            time.sleep(2)
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
        self.position = 1
        self.speedq = Queue()
        
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
        logging.debug("Player Created")
        self.accel_server.loop_start()
        while True:
            time.sleep(5)
    
    def threadstart(self):
        self.speedthread.start()
        self.startthread.start()

    # MQTT Callbacks    
    def on_subscribe_accel(self, client, userdata, mid, granted_qos):
        logging.debug("Accel Subscribed: "+str(mid)+" "+str(granted_qos))

    def on_message_accel(self, client, userdata, msg):
        logging.debug(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))  
        speed = int(msg.payload.decode("utf-8"))
        self.speedq.put(speed)
        
    def on_connect_accel(self, client, obj, flags, rc):
        if rc == 0:
            logging.debug("Accel connected")
            # not working bc playername is not just "Device" its b'Device
            client.subscribe("info/speed/"+self.playername, qos = 1)
        else:
            logging.debug("Bad connection")
    
    # Handlers 
    def handle_speed(self):
        while True:
            while not self.speedq.empty():
                speed = self.speedq.get()
                self.calcDist(int(speed))

    def calcDist(self, newspeed):
        self.prev_speed = self.speed 
        self.speed = newspeed
        self.dist += 1/2*(self.speed + self.prev_speed)*0.1 # timestep

def main():
    Game("localhost", 1883)

if __name__ == "__main__":
    main()