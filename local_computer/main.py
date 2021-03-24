from fpga_uart import uart_handler 
from mqtt_client import mqtt_client
from game import Game 
import threading
import argparse
import config

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
    
    ########## Initialising Global Data Structures
    config.ready_flag.clear()
    config.start_flag.clear()
    config.start_queue_flag.clear()
    config.final_flag.clear()
    config.end_flag.clear()
    config.send_bomb_flag.clear()
    config.bp_flag.clear()
    config.bombed_flag.clear()
    

    fpga_thread = threading.Thread(name = "fpga-thread",target=uart_handler, args=('n', args.wsl))

    # Start Thread for MQTT Client Start Client     
    mqtt = mqtt_client(args.serverip, int(args.port), args.username, args.password, args.encrypt)
    mqtt.connect()
    mqtt_thread = threading.Thread(name = "mqtt-thread", target=mqtt.start_client)    
    
    # Start Thread for game
    new_game = Game() 
    
    fpga_thread.daemon = True
    mqtt_thread.daemon = True
    
    mqtt_thread.start()
    fpga_thread.start()
    new_game.game_start()
