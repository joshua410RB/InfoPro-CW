import socket
import threading, queue
from random import randint
import time
import logging
import subprocess

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

test_data = queue.Queue()

def generate_random():
    logging.debug("Starting Generation")
    index = 0
    while True:
        test_data.append(randint(0,10))
        time.sleep(0.1)
        # if (index == 1000):
        #     break
        index += 1
    logging.debug("Exiting Generation")


def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def receive_val(cmd):
    logging.debug("Starting FPGA UART")
    inputCmd = "nios2-terminal.exe <<< {}".format(cmd)
 
    process = subprocess.Popen(inputCmd, shell=True, executable='/bin/bash' , stdout=subprocess.PIPE)
    index = 0
    while True:
        output = process.stdout.readline()
        # if process.poll() is not None and output == b'':
        #     break
        output = output.decode("utf-8")
        tmp = output.split()
        try:
            
            if (len(tmp[-1]) == 8):
                out = twos_comp(int(tmp[-1],16), 32)
                test_data.put(-1*int(out))
                # print(tmp[-1])
                # print(test_data)
        except:
            pass  
        # if (index == 999):
        #     break    
        index += 1
    
    logging.debug("Closing UART")

def start_client():
    logging.debug("Starting Client")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        index = 0
        while True:
            try:
                item = test_data.get()
                logging.debug(item)
                sent = s.send(item.to_bytes(4,"big"))
            except IndexError:
                logging.debug("Waiting")
                time.sleep(0.01)
                # sent = s.send(test_data[index].to_bytes(4,"big"))
                
            # data = s.recv(1024)
            # print('Received', int.from_bytes(data, "big"))
            index += 1
            # if (index == 1000):
            #     break
    logging.debug("Exiting Client")


def main():
    x = threading.Thread(target=receive_val, args={'o'})
    # x = threading.Thread(target=generate_random)
    # receive_val("o")
    y = threading.Thread(target=start_client)
    x.start()
    y.start()

    x.join()
    y.join()

if __name__ == '__main__':
    main()