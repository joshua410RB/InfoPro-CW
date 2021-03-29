# InfoPro-CW

## How to use
1. Server Set Up
- In the docker container, do
```
./run_server.sh
```

This will initialise the server database and start the server client

2. Client Set Up

To run the client, there are a few steps: 

- Enable the ```nios2-terminal``` by running the ```nios2_command_shell.sh``` in your Quartus installation

- To start the game, run
```
python3 local_computer/main.py --serverip _serverip_ -- port 32552 --username _username_ -e -w
```

- ```serverip``` is your server's ip address, but if running in siyu's AWS server, the ```serverip``` will be _infopro.lioneltsy.life_
- ```port``` is the port of the server that the client is connecting to
- Use the ```-e``` argument if you want to encrypt the connection
- Use the ```w``` argument if the script is ran in a WSL environemnt


3. FPGA Set Up
- The ```.sof``` and ```.elf``` files in the ```hardware/sof_elf``` folder can be used directly to blast and program the FPGA. 
- To blast and program the FPGA, use the commands:
```
nios2-configure-sof hardware/sof_elf
nios2-download -g hardware/sof_elf/16tap.elf
```
- Other working files are stored in ```hardware/quartus_files``` 

## Testing
1. FPGA UART Connection Test

2. Server Connection/Load Test
- The ```local_computer/test_client_server.py``` script is used to perform testing. To perform testing, run 
```
python3 local_computer/test_client_server.py --testno _testno_
```

```testno``` is used to specify the number of clients that will be simulated. 

- For average response time testing, run
```
python3 local_computer/test_server_response.py
```

This script generates 2 clients with a fixed distance target. A client will be the bomb sender, and the other, the receiver. The duration between the bomb being sent and the bomb received by the other client is obtained.