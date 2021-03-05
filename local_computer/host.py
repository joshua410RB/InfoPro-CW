import subprocess
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime as dt
import threading
import time
xs = []
ys = []

def receive_val(cmd):
    inputCmd = "nios2-terminal.exe <<< {}".format(cmd)
 
    process = subprocess.Popen(inputCmd, shell=True, executable='/bin/bash' , stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        # if process.poll() is not None and output == b'':
        #     break
        output = output.decode("utf-8")
        tmp = output.split()
        try:
            
            if (len(tmp[-1]) == 8):
                out = twos_comp(int(tmp[-1],16), 32)
                # print(out)
                xs.append(dt.datetime.now().strftime("%H:%M:%S.%f"))
                ys.append(out)
                # print(tmp[-1])
        except:
            pass      

    # retval = process.poll()   # vals = str(output.stdout)

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

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
    plt.ylim((-300,100))
    plt.grid()

def main():
    # put your code here ...
    fig,ax = plt.subplots()
    x = threading.Thread(target=receive_val, args={"f"})
    x.start()
    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys, ax), interval=1000)
    plt.show()

    
if __name__ == '__main__':
    main()
