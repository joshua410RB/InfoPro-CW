from fpga_uart import uart_handler 
from mqtt_client import mqtt_client
from game_2 import Game 
import threading
import queue
import sys

if __name__ == "__main__":


    # Start Thread for FPGA UART Connection
    x_data = queue.Queue()
    y_game_data = queue.Queue()
    y_mqtt_data = queue.Queue()
    fpga_thread = threading.Thread(target=uart_handler, args=('o',x_data,y_game_data, y_mqtt_data))

    # Start Thread for MQTT Client Start Client     
    mqtt = mqtt_client("localhost", 1883, "siting", y_mqtt_data)
    mqtt.connect()
    mqtt_thread = threading.Thread(target=mqtt.start_client)    
    
    # Start Thread for game
    new_game = Game(x_data, y_game_data)
    game_thread = threading.Thread(target=new_game.game_start)
    
    mqtt_thread.start()
    fpga_thread.start()
    game_thread.start()