import time
import subprocess
import logging
from collections import deque
import re
import pexpect
import sys
import threading
import config
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime as dt
xs = []
ys = []

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

# assumes linear acceleration between speed datas
def calcDist(dist, prevspeed, newspeed):
    dist += 1/2*(newspeed + prevspeed)*0.1 # timestep
    return dist

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is


def uart_handler(cmd, wsl):
    logging.debug("Starting FPGA UART")
    if wsl:
        inputCmd = "nios2-terminal.exe <<< {}".format(cmd)
        proc = pexpect.spawn('/bin/bash',['-c', inputCmd])    # logfile=sys.stdout
    else:
        proc = pexpect.spawn('nios2-terminal')    # logfile=sys.stdout
        proc.expect("Use the IDE stop button or Ctrl-C to terminate")
    
    start_time = time.time()
    # Ignore first few Inputs
    inner_index = 0
    while inner_index < 5:
        inner_index += 1
        proc.readline()

    # calcualting dist variables
    prevspeed = 0
    # Start off with Normal Mode
    proc.send("n")
    index = 0
    sent_slow = sent_normal = False
    
    while True:
        current_time = time.time()
        # print(start_time, current_time)
        output = proc.readline().decode('utf-8')            

        ############# Finding frame        
        try:
            find_frame = re.split('<->|<\|>', output)[1]
            values = find_frame.split("|")
            # logging.debug(values)
        except:
            proc.close()
            logging.debug("FPGA UART Connection Failed")
            break

        ############ Handle Button

        button_pressed = int(values[3])
        # button_pressed =0
        if button_pressed == 1:
            config.bp_flag.set()
            logging.debug("Button Pressed !!!!!")
            
        if current_time - start_time > 0.005:
        # if True:
            # logging.debug(output)

            ############ Getting x, y, z data
            try:       
                current_x = int(values[0],16)
                current_y = int(values[1],16)
                current_z = int(values[2],16)

                # logging.debug(str(current_x)+", "+str(current_y))
                converted_x = (current_x-32768)
                converted_y = (current_y-32768)
                converted_z = current_z
            except:
                logging.debug("Could not convert values")
                pass

            # logging.debug("Converted vals: " + str(converted_x) + ", "+ str(converted_y) +", "+ str(converted_z))

            ########### Scaling x, y, z values based on the game
            scaled_x = (-converted_x+256)/512*900
            if scaled_x < 80:
                scaled_x = 80
            elif scaled_x > 700:
                scaled_x = 700
            scaled_y = (-converted_y+256)//30
            if scaled_y < 3:
                scaled_y = 3
            elif scaled_y > 20:
                scaled_y = 20

            # logging.debug("Scaled Vals: "+ str(scaled_x) + ", "+ str(scaled_y) )
            # xs.append(dt.datetime.now().strftime("%H:%M:%S.%f"))
            # ys.append(scaled_x)
            # logging.debug(xs)
            # logging.debug(ys)

            ########## Update Global Data Structures for other threads
            if config.start_queue_flag.is_set() and not config.end_flag.is_set():
                # x_data.append((-converted_x+250)/600*900)
                # y_game_data.append((-converted_y+250)//30)
                
                config.x_data_deque.append(scaled_x)
                config.y_game_data_deque.append(scaled_y)
                # y_mqtt_data.append((-converted_y+250)//30)

                config.dist_data = calcDist(config.dist_data, prevspeed, scaled_y)
                # logging.debug("UART Changing dist: " + str(config.dist_data))
                prevspeed = scaled_y
            


        

            ########### Check current player status
            if not wsl:
                # Send Data to change mode
                if config.bombed_flag.is_set():
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

            start_time = current_time
        index += 1

    
    logging.debug("Closing UART")
    
def animate(i, xs, ys, ax):
    # Limit x and y lists to 20 items
    xs = xs[-50:]
    ys = ys[-50:]

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys)
    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.title('Accelerometer Sensor Values Over Time')
    plt.ylabel('Accelerometer Value')
    plt.xlabel('Time (s)')
    plt.ylim((-100,1000))
    plt.grid()

def main():
    # put your code here ...
    fig,ax = plt.subplots()
    x = threading.Thread(target=uart_handler, args={"n",True})
    x.start()
    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys, ax), interval=1000)
    plt.show()

if __name__ == "__main__":
    config.start_queue_flag.set()
    uart_handler('n',False)
    # main()