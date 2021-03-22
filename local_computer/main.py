from fpga_uart import uart_handler 
from mqtt_client import mqtt_client
from game import Game 
import threading
try: 
    import queue
except ImportError:
    import Queue as queue
import argparse

# global variable for accelerometer data
x_data_unsafe=0
y_data_unsafe=0
z_data_unsafe=0
switch_data_unsafe=0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Racing Game')
    parser.add_argument('--serverip', 
                        default="localhost",
                        help='input your server ip')
    parser.add_argument('--port', 
                        default= 1883,
                        help='input your server port')
    parser.add_argument('--username', 
                        default="player",
                        help='input your game username')
    parser.add_argument('--password', 
                        help='input your game password')

    args = parser.parse_args()
    print(args.serverip)
    print(args.port)
    print(args.username)
    print(args.password)
    # Start Thread for FPGA UART Connection
    x_data = queue.Queue()
    # x_data = []
    y_game_data = queue.Queue()
    y_mqtt_data = queue.Queue()
    #Ready Event => From game to mqtt
    ready_flag = threading.Event()
    #Start Event => mqtt to game and fpga thread
    start_flag = threading.Event()
    start_queue_flag = threading.Event() #needed cos of countdown
    #Final Event => mqtt to game
    final_flag = threading.Event()
    #Ready Object => mqtt to game
    ready_object = {}
    #Leaderboard Object => mqtt to game
    leaderboard_object = {}
    #End Game Event => Game to FPGA and MQTT
    end_flag = threading.Event()

    fpga_thread = threading.Thread(target=uart_handler, args=('o',x_data,y_game_data, y_mqtt_data, start_queue_flag, end_flag))

    # Start Thread for MQTT Client Start Client     
    mqtt = mqtt_client(args.serverip, args.port, args.username, args.password, 
                        y_mqtt_data, ready_flag, start_flag, final_flag, 
                        leaderboard_object, ready_object, end_flag)
    mqtt.connect()
    mqtt_thread = threading.Thread(target=mqtt.start_client)    
    
    # Start Thread for game
    new_game = Game(x_data, y_game_data, 
                    ready_flag, start_flag, start_queue_flag, final_flag, 
                    leaderboard_object, ready_object, end_flag)
    
    fpga_thread.daemon = True
    mqtt_thread.daemon = True
    
    mqtt_thread.start()
    fpga_thread.start()
    new_game.game_start()
