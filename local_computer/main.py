from fpga_uart import uart_handler 
from mqtt_client import mqtt_client
from game_2 import Game 
import threading
import queue
import sys

# global variable for accelerometer data
x_data_unsafe=0
y_data_unsafe=0
z_data_unsafe=0
switch_data_unsafe=0

if __name__ == "__main__":


    # Start Thread for FPGA UART Connection
    x_data = queue.Queue()
    y_game_data = queue.Queue()
    y_mqtt_data = queue.Queue()
    #Ready Event => From game to mqtt
    ready_flag = threading.Event()
    #Start Event => mqtt to game and fpga thread
    start_flag = threading.Event()
    #Leaderboard Object => mqtt to game
    leaderboard_object = {}
    #End Game Event => Game to FPGA and MQTT
    end_flag = threading.Event()

    fpga_thread = threading.Thread(target=uart_handler, args=('o',x_data,y_game_data, y_mqtt_data, start_flag, end_flag))

    # Start Thread for MQTT Client Start Client     
    mqtt = mqtt_client("localhost", 1883, "siting", y_mqtt_data, ready_flag, start_flag, leaderboard_object, end_flag)
    mqtt.connect()
    mqtt_thread = threading.Thread(target=mqtt.start_client)    
    
    # Start Thread for game
    new_game = Game(x_data, y_game_data, ready_flag, start_flag, leaderboard_object, end_flag)
    
    fpga_thread.daemon = True
    mqtt_thread.daemon = True
    
    mqtt_thread.start()
    fpga_thread.start()
    new_game.game_start()