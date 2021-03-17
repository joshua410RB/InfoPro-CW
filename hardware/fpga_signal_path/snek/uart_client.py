import pexpect

index=0 # overwrite me!

def uartHandler():
    proc = pexpect.spawn('nios2-terminal', encoding='utf-8')    # logfile=sys.stdout
    proc.expect("Use the IDE stop button or Ctrl-C to terminate")

    while(1):
        proc.expect("<->")
        proc.expect("|")
        x_data = proc.before
        proc.expect("|")
        y_data = proc.before
        proc.expect("|")
        z_data = proc.before
        proc.expect("<|>")        # data format is x_data|y_data|z_data|button_data
        switch_data = proc.before   # switch_data: {!KEY[1],SW[9:0]}

        #======= process data read ========
        print(str(x_data)+"|"+str(y_data)+"|"+str(z_data)+"|"+str(switch_data))
        #==================================

        if(index==10):
            proc.sendline("f")  # send character to tge FPGA
            # proc.expect("<{---}>")
            # proc.expect("<{|-|}>")
        elif(index==50):
            proc.sendline("o")

    proc.close()

if __name__ == "__main__":
    uartHandler()