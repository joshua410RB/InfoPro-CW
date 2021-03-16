import paho.mqtt.client as paho
import time
import threading,queue
import logging
from random import randint
import subprocess

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )
speed_data = queue.Queue()
current_mode = threading.Event()
mode_change = threading.Condition()

# ----------------MQTT Settings-----------------

def on_publish(client, userdata, mid):
    logging.debug("publishing message no.: "+str(mid))
    pass

def on_connect_accel(client, obj, flags, rc):
    if rc == 0:
        logging.debug("Accel connected")
    else:
        logging.debug("Bad connection")

def on_connect_bomb(client, obj, flags, rc):
    if rc == 0:
        logging.debug("Bomb connected")
        client.subscribe("info/bomb", qos = 1)
    else:
        logging.debug("Bad connection")

def on_message(client, obj, msg):
    logging.debug(msg.topic + " " + str(msg.payload))

class mqtt_client:
    def __init__(self, ip, port):
        self.brokerip = ip
        self.brokerport = port
        self.accel_client = paho.Client("node1")
        self.bomb_client = paho.Client("node2")
        self.accel_client.on_connect = on_connect_accel
        self.bomb_client.on_connect = on_connect_bomb
        self.accel_client.on_publish = on_publish
        self.bomb_client.on_message = on_message

    def connect(self):
        try:
            self.accel_client.connect(self.brokerip, self.brokerport)
            self.bomb_client.connect(self.brokerip, self.brokerport)        

        except:
            logging.debug("Connection Failed")
            exit(1)

    def start_client(self):
        logging.debug("Client Started")
        self.bomb_client.loop_start()
        self.accel_client.loop_start()
        while True:
            sensor_data = speed_data.get()
            self.accel_client.publish("info/speed", "Device1:"+str(sensor_data), qos=1)
            # time.sleep(0.5)
            logging.debug(sensor_data)

# ----------------UART Data-----------------
def generate_random():
    logging.debug("Starting Generation")
    index = 0
    while True:
        speed_data.put(randint(0,10))
        time.sleep(0.5)
        if (index == 1000):
            break
        index += 1
    logging.debug("Exiting Generation")

def receive_val(cmd):
    logging.debug("Starting FPGA UART")
    inputCmd = "nios2-terminal.exe <<< {}".format(cmd)
 
    process = subprocess.Popen(inputCmd, shell=True,
                                executable='/bin/bash' , 
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
    index = 0
    while True:
        output = process.stdout.readline()
        # if process.poll() is not None and output == b'':
        #     break
        time.sleep(0.5)
        output = output.decode("utf-8")
        tmp = output.split()
        logging.debug(tmp)
        try:
            # if (len(tmp[-1]) == 8):
            out = twos_comp(int(tmp[-1],16), 32)
            absolute_out = -1 * int(out)
            speed_data.put(absolute_out)
            move = absolute_out / 300 * 800
            # print(move)
            # movement_data.append(move)
            # print(tmp[-1])
            # print(speed_data)
        except:
            pass  
        if (index == 50):
            # stdout_val = process.communicate(input="o".encode())[0]
            
            # logging.debug(stdout_val.decode('utf-8'))
            break
        elif (index == 10):
            stdout_val = process.communicate(input="f".encode())[0]
            print(stdout_val)
            # process.stdin.write(b'f\n')
            # process.stdin.flush()
            # print(process.stdout.readline())
            logging.debug("Sending mode")
        index += 1
    
    logging.debug("Closing UART")

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def main():
    receive_val("o")
    # mqtt = mqtt_client("localhost", 1883)
    # mqtt.connect()
    # # x = threading.Thread(target=generate_random)
    # x = threading.Thread(target=receive_val, args={'o'})
    # # y = threading.Thread(target=mqtt.start_client)
    # x.start()
    # y.start()

if __name__ == "__main__":
    main()