from fpga_uart import uart_handler 
from mqtt_client import mqtt_client
from game import Game 
import threading
from multiprocessing import Queue
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
    parser.add_argument('-e', '--encrypt', action='store_true',
                        help='Use encryption using TLS')
    parser.add_argument('-w', '--wsl', action='store_true',
                        help='Playing on WSL')
    args = parser.parse_args()
    print("Welcome {}".format(args.username))
    print("Attempting to connect to {} via {}".format(args.serverip, args.port))
    # Start Thread for FPGA UART Connection
    x_data = Queue()
    # x_data = []
    y_game_data = Queue()
    y_mqtt_data = Queue()
    #Ready Event => From game to mqtt
    ready_flag = threading.Event()
    #Start Event => mqtt to game and fpga thread
    start_flag = threading.Event()
    start_queue_flag = threading.Event() #needed cos of countdown
    start_queue_flag.clear()
    #Final Event => mqtt to game
    final_flag = threading.Event()
    final_flag.clear()
    #Ready Object => mqtt to game
    ready_object = {}
    #Leaderboard Object => mqtt to game
    leaderboard_object = {}
    #End Game Event => Game to FPGA and MQTT
    end_flag = threading.Event()
    end_flag.clear()
    #Send bomb => Game to MQTT
    send_bomb_flag = threading.Event()
    #Bomb button press => FPGA to Game
    bp_flag = threading.Event()
    bp_flag.clear()
    # got bombed => MQTT to Game and FPGA
    bombed_flag = threading.Event()
    bombed_flag.clear()

    fpga_thread = threading.Thread(target=uart_handler, args=('o',x_data,y_game_data, y_mqtt_data, start_queue_flag, end_flag, bp_flag, bombed_flag, args.wsl))

    # Start Thread for MQTT Client Start Client     
    mqtt = mqtt_client(args.serverip, int(args.port), args.username, args.password, args.encrypt,
                        y_mqtt_data, ready_flag, start_flag, final_flag, 
                        leaderboard_object, ready_object, end_flag, send_bomb_flag, bombed_flag)
    mqtt.connect()
    mqtt_thread = threading.Thread(target=mqtt.start_client)    
    
    # Start Thread for game
    new_game = Game(x_data, y_game_data, 
                    ready_flag, start_flag, start_queue_flag, final_flag, 
                    leaderboard_object, ready_object, end_flag, bp_flag, send_bomb_flag, bombed_flag)
    
    fpga_thread.daemon = True
    mqtt_thread.daemon = True
    
    mqtt_thread.start()
    fpga_thread.start()
    new_game.game_start()
