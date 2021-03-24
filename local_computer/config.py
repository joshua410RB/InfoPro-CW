from collections import deque
import threading

######### Global Data Structures shared between Threads
# Start Thread for FPGA UART Connection
x_data = 0
x_data_deque = deque()

y_game_data = 0
y_game_data_deque = deque()

dist_data = 0

highscore_object = {}

######### Threading Flags
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

#Send bomb => Game to MQTT
send_bomb_flag = threading.Event()

#Bomb button press => FPGA to Game
bp_flag = threading.Event()

# got bombed => MQTT to Game and FPGA
bombed_flag = threading.Event()