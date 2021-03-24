import time
import subprocess
import logging
from collections import deque
import re
import pexpect
import sys
import threading
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )


def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is


def uart_handler(cmd, x_data, y_game_data, y_mqtt_data, start_queue_flag, end_flag, bp_flag, bombed_flag, wsl):
    logging.debug("Starting FPGA UART")
    if wsl:
        inputCmd = "nios2-terminal.exe <<< {}".format(cmd)
        proc = pexpect.spawn('/bin/bash',['-c', inputCmd])    # logfile=sys.stdout
    else:
        proc = pexpect.spawn('nios2-terminal')    # logfile=sys.stdout
        proc.expect("Use the IDE stop button or Ctrl-C to terminate")
    
    # Ignore first few Inputs
    inner_index = 0
    while inner_index < 5:
        inner_index += 1
        proc.readline()

    # Start off with Normal Mode
    proc.send("n")
    index = 0
    sent_slow = sent_normal = False
    start_time = time.time()
    while True:
        output = proc.readline().decode('utf-8')
        # logging.debug(output)
        tmp = re.split('; |, |<->|<|>:|\r|\n\|', output)
        tmp = tmp[1].split("|")
        # logging.debug(tmp)
        # Receive Data
        current_x = tmp[0]
        current_y = tmp[1]
        current_z = tmp[2]
        # button_pressed = int(tmp[3])
        button_pressed =0 
        if button_pressed == 1:
            bp_flag.set()
        elif button_pressed == 0:
            bp_flag.clear()
        # logging.debug(current_x+", "+current_y)
        converted_x = twos_comp(int(current_x, 16),16)
        converted_y = twos_comp(int(current_y, 16),16)
        converted_z = twos_comp(int(current_z, 16),16)
        current_time = time.time()
        if current_time - start_time > 0.005:
        # if True:
            logging.debug(str((-converted_x+250)/600*900)+", "+str(-converted_y+250)+", "+str(-converted_z+250)+", "+str(button_pressed))
            try:
                if start_queue_flag.is_set() and not end_flag.is_set():
                    logging.debug("Putting values in queue from fpga")
                    x_data.append((-converted_x+250)/600*900)
                    y_game_data.append((-converted_y+250)//30)
                    y_mqtt_data.append((-converted_y+250)//30)
            except:
                pass  
            start_time = current_time
        
        if wsl:
            # Send Data to change mode
            if bombed_flag.is_set():
                # Bomb received, change to slow mode
                if not sent_slow:
                    logging.debug("Slowed")
                    proc.send("s")
                    sent_slow = True
                    sent_normal = False
            else:
                # back to normal
                if not sent_normal:
                    logging.debug("Normal Speed")
                    proc.send("n")
                    sent_normal = True
                    sent_slow = False

        index += 1
    
    logging.debug("Closing UART")



# def uart_handler(cmd, x_data, y_game_data, y_mqtt_data, start_queue_flag, end_flag, bp_flag, bombed_flag):
#     logging.debug("Starting FPGA UART")
#     inputCmd = "nios2-terminal <<< {}".format(cmd)
 
#     process = subprocess.Popen(inputCmd, shell=True,
#                                 executable='/bin/bash' , 
#                                 stdin=subprocess.PIPE,
#                                 stdout=subprocess.PIPE)
#     index = 0
#     while True:
#         output = process.stdout.readline()
#         # if process.poll() is not None and output == b'':
#         #     break
#         output = output.decode("utf-8")
#         logging.debug(output)
#         if (index >5):
#             tmp = re.split('; |, |<->|<|>:|\r|\n\|', output)
#             tmp = tmp[1].split("|")
#             logging.debug(tmp)
#             if len(tmp) > 2:
#                 current_x = tmp[0]
#                 current_y = tmp[1]
#                 button_pressed = tmp[2]
#                 if button_pressed == 1:
#                     bp_flag.set()
#                 elif button_pressed == 0:
#                     bp_flag.clear()
#                 logging.debug(current_x+", "+current_y)
#                 converted_x = twos_comp(int(current_x, 16),16)
#                 converted_y = twos_comp(int(current_y, 16),16)
#                 logging.debug(str(-converted_x)+", "+str(-converted_y))
#                 logging.debug(str((-converted_x+250)/600*900)+", "+str(-converted_y+250))
#                 try:
#                     if start_queue_flag.is_set() and not end_flag.is_set():
#                         logging.debug("Putting values in queue from fpga")
#                         # x_data.put((-converted_x+250)/600*900)
#                         x_data.append((-converted_x+250)/600*900)
#                         y_mqtt_data.put((-converted_y+250)//30)
#                         y_game_data.put((-converted_y+250)//30)
#                 except:
#                     pass  
                    

#         index += 1
    
#     logging.debug("Closing UART")
if __name__ == "__main__":
    x_data = deque()
    y_game_data = deque()
    y_mqtt_data = deque()
    start_flag = threading.Event()
    start_flag.clear()
    end_flag = threading.Event()
    end_flag.clear()
    bombed_flag = threading.Event()
    bombed_flag.clear()
    bp_flag = threading.Event()
    bp_flag.clear()
    uart_handler('o',x_data,y_game_data, y_mqtt_data,start_flag, end_flag, bp_flag, bombed_flag, True)