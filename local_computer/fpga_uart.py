import time
import subprocess
import logging
import queue 
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


def uart_handler(cmd, x_data, y_game_data, y_mqtt_data, start_queue_flag, end_flag, bp_flag, bombed_flag):
    logging.debug("Starting FPGA UART")
    inputCmd = "nios2-terminal <<< {}".format(cmd)
 
    process = subprocess.Popen(inputCmd, shell=True,
                                executable='/bin/bash' , 
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
    index = 0
    while True:
        output = process.stdout.readline()
        # if process.poll() is not None and output == b'':
        #     break
        output = output.decode("utf-8")
        logging.debug(output)
        if (index >5):
            tmp = re.split('; |, |<->|<|>:|\r|\n\|', output)
            tmp = tmp[1].split("|")
            logging.debug(tmp)
            if len(tmp) > 2:
                current_x = tmp[0]
                current_y = tmp[1]
                button_pressed = tmp[2]
                if button_pressed == 1:
                    bp_flag.set()
                elif button_pressed == 0:
                    bp_flag.clear()
                logging.debug(current_x+", "+current_y)
                converted_x = twos_comp(int(current_x, 16),16)
                converted_y = twos_comp(int(current_y, 16),16)
                logging.debug(str(-converted_x)+", "+str(-converted_y))
                logging.debug(str((-converted_x+250)/600*900)+", "+str(-converted_y+250))
                try:
                    if start_queue_flag.is_set() and not end_flag.is_set():
                        logging.debug("Putting values in queue from fpga")
                        # x_data.put((-converted_x+250)/600*900)
                        x_data.append((-converted_x+250)/600*900)
                        y_mqtt_data.put((-converted_y+250)//30)
                        y_game_data.put((-converted_y+250)//30)
                except:
                    pass  
                    

        index += 1
    
    logging.debug("Closing UART")

def uartHandler_pexpect():
    new_input = False
    while True:
        if new_input:
            proc = pexpect.spawn('nios2-terminal')    # logfile=sys.stdout
            proc.expect("Use the IDE stop button or Ctrl-C to terminate")

        index = 0
        while index < 4:
            logging.debug(proc.readline())
            index += 1
        logging.debug("Getting data")

        if index 
        proc.sendline("o")
        while(1):
            time.sleep(1)
            output = proc.readline().decode('utf-8')
            tmp = re.split(';|<|>|-|, |:|\|', output)
            logging.debug(str(index) + ": " +output)
            # if len(tmp) > 4:
            #     current_x = tmp[3]
            #     current_y = tmp[4]
            #     # logging.debug(current_x+", "+current_y)
            #     converted_x = twos_comp(int(current_x, 16),32)
            #     converted_y = twos_comp(int(current_y, 16),32)
            #     # logging.debug(str(-converted_x)+", "+str(-converted_y))
            #     logging.debug(str((-converted_x+250)/600*900)+", "+str(-converted_y+250))
            #     try:
            #         x_data.put((-converted_x+250)/600*900)
            #         y_mqtt_data.put(-converted_y+250)
            #         y_game_data.put(-converted_y+250)
            #     except:
            #         pass  
            if(index==10):
                proc.sendline("f")  # send character to tge FPGA
                logging.debug("Filter Off")
                # proc.expect("<{---}>")
                # proc.expect("<{|-|}>")
            elif(index==50):
                proc.sendline("o")
            index += 1

        proc.close()

def uart_handler_subprocess():
    logging.debug("Starting FPGA UART")
    inputCmd = "nios2-terminal <<< {}".format('o')
 
    process = subprocess.Popen(inputCmd, shell=True,
                                executable='/bin/bash' , 
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
    index = 0
    while True:
        output = process.stdout.readline()

        output = output.decode("utf-8")
        logging.debug(output)

        if index == 10:
            print("Changing Filter")
            process.stdin.write(b'f')
            time.sleep(1)
        index += 1
    
    logging.debug("Closing UART")

if __name__ == "__main__":
    x_data = queue.Queue()
    y_game_data = queue.Queue()
    y_mqtt_data = queue.Queue()
    start_flag = threading.Event()
    start_flag.clear()
    end_flag = threading.Event()
    end_flag.clear()
    bombed_flag = threading.Event()
    bombed_flag.clear()
    bp_flag = threading.Event()
    bp_flag.clear()
    # uart_handler('o',x_data,y_game_data, y_mqtt_data,start_flag, end_flag, bp_flag, bombed_flag)
    # uartHandler_pexpect()
    uart_handler_subprocess()