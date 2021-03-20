from fpga_uart import uart_handler 
from mqtt_client import mqtt_client
from game_2 import Game 
import threading
import queue
import sys

if __name__ == "__main__":
    # Set Up MQTT Client
    # mqtt = mqtt_client("localhost", 1883, "siting")
    # mqtt.connect()

    # Start Thread for FPGA UART Connection
    x_data = queue.Queue()
    y_data = queue.Queue()
    fpga_thread = threading.Thread(target=uart_handler, args=('o',x_data,y_data))

    # Start Thread for MQTT Client Start Client 
    # mqtt_thread = threading.Thread(target=mqtt.start_client)
    
    # Start Thread for game
    new_game = Game(x_data, y_data)
    game_thread = threading.Thread(target=new_game.game_start)
    
    # mqtt_thread.start()
    fpga_thread.start()
    game_thread.start()