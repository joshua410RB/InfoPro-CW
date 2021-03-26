import sys
import config
import fpga_uart
import threading
import time

proc = threading.Thread(target=fpga_uart.uart_handler, args=('n', 0), name='Test_Thread')
proc.daemon=True
proc.start()

print("starting test")
print("checking for UART connection")
time.sleep(2)
if not proc.is_alive:
    print("connection/nios2-terminal failed")
    sys.exit(1)
print("Connection succeed")
xPass=0
yPass=0
bombPass=0
testPass=1
print("Testing x-axis")
config.start_queue_flag.set()
print("move fpga in x-axis")
startTime = time.time()
prevData=0
while (time.time()-startTime)<3:
    if(len(config.x_data_deque)>0):
        data=config.x_data_deque.pop()
        if data!=prevData:
            xPass=1
        prevData=data
if xPass==1:
    print("x-axis passed")
else:
    print("x-axis failed")
time.sleep(0.5)

print("Testing y-axis")
print("move fpga in y-axis")
startTime = time.time()
prevData=0
while (time.time()-startTime)<3:
    if(len(config.y_game_data_deque)>0):
        data=config.y_game_data_deque.pop()
        if data!=prevData:
            yPass=1
        prevData=data
if yPass==1:
    print("y-axis passed")
else:
    print("y-axis failed")
time.sleep(0.5)

print("Testing bomb button")
print("spam press bomb button")
startTime = time.time()
prevData=0
while (time.time()-startTime)<3:
    if config.bp_flag.is_set():
        bombPass=1
if bombPass==1:
    print("bomb test passed")
else:
    print("bomb testfailed")
time.sleep(0.5)

if xPass==0:
    print("x-axis read fail1")
    testPass=0
if yPass==0:
    print("y-axis read fail")
    testPass=0
if bombPass==0:
    print("PACIFIST (y u no use bomb)")
    testPass=0
if testPass==0:
    print("FPGA UART handler failed")
else:
    print("all tests passed! :)")