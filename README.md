# InfoPro-CW

## How to use
1. Server Set Up
- In the docker container, do
```
./run_server.sh
```

This will initialise the server database and start the server client

2. Client Set Up
- On your own local computer, do 

```
./launch_client.sh
```

This will start your ```nios2_command_shell``` that is necessary for uart communication

```main.py``` is then ran to start the game interface, the fpga uart script and the mqtt client.

3. FPGA Set Up
- The ```.sof``` and ```.elf``` files in the ```hardware/sof_elf``` folder can be used directly to blast and program the FPGA. 
- Other working files are stored in ```hardware/quartus_files``` 

## Testing
1. FPGA UART Connection Test

2. Server Connection/Load Test
- The ```local_computer/test_client_server.py``` script is used to perform testing. To perform testing, run 
```
python3 local_computer/test_client_server.py --testno _testno_
```

_testno_ is used to specify the number of clients that will be simulated. 

In the script, based on the specified number of clients, 