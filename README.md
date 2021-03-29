# InfoPro-CW

## How to use
### Server Set Up
Our server implementation uses Docker to deploy. It will start the broker and run mqtt_server.py which is the server handler.
TLS encryption is implemented using self-signed certs with the server as the Certificate Authority. A copy of the server's CA cert is shared with the local computer. If you would like to use the Encrypted Version, you will either have to create your own certificates or approach one of the team members to start our server. Else, run the unencrypted version.
To deploy the server, in your cloud instance, install Docker and run the following commands in the server folder:
- With Encryption
```
docker build . -t infopro_server:1.0 --file Dockerfile
docker run -it --rm -p 0.0.0.0:32552:8883/tcp infopro_server:1.0
```
- Without Encryption
```
docker build . -t infopro_server:1.0 --file Dockerfile_NoEncrypt
docker run -it --rm -p 0.0.0.0:32552:1883/tcp infopro_server:1.0 
```
This will initialise the server database and start the server client. 

### FPGA Set Up
- The ```.sof``` and ```.elf``` files in the ```hardware/sof_elf``` folder can be used directly to blast and program the FPGA. 
- To blast and program the FPGA, use the commands in the ```hardware/sof_elf``` directory:
```
nios2-configure-sof 16_tap.sof
nios2-download -g 16_tap.elf
```
- Other working files are stored in ```hardware/quartus_files``` for reference.

### Client Set Up

- Enable the ```nios2-terminal``` by running the ```nios2_command_shell.sh``` in your Quartus installation directory.
- Run ```pip3 install -r requirements.txt``` in the local_computer directory.

- To start the game, run
```
python3 local_computer/main.py --serverip _serverip_ -- port 32552 --username _username_ -e -w
```

- ```serverip``` is your server's ip address, but if running in siyu's AWS server, the ```serverip``` will be _infopro.lioneltsy.life_
- ```port``` is the port of the server that the client is connecting to
- Use the ```-e``` argument if you want enable encryption on the server connection
- Use the ```-w``` argument if the script is ran in a WSL environemnt

## Testing
1. **FPGA UART Connection Test**

- The ```local_computer/test_uart_handler.py``` script interfaces to the uart_handler function and requests certain actions from the user, subsequently verifying if the data is streamed correctly to the appropriate channels based on that. 
Before running this script, make sure that the FPGA has been set up and blasted with the necessary software.

2. **Load Test**

- The ```local_computer/test_client_server.py``` script is used to perform load testing. To perform testing, run 
```
python3 local_computer/test_client_server.py --testno _testno_ --serverip _serverip_ --port _port_
```

- ```testno``` is used to specify the number of clients that will be simulated
- ```serverip``` is used to specify the ip address of your server 
- ```port``` is used to specify the port number that you opened on your server


3.  **Server Response Time Test**
- To run the response time test, use
```
python3 local_computer/test_server_response.py --serverip _serverip_ --port _port_
```
- This script generates 2 clients with a fixed distance target. A client will be the bomb sender, and the other, the receiver. The duration between the bomb being sent and the bomb received by the other client is obtained.

## The Team
- Si Yu Tan
- Joshua Lim
- Zhao Siting
- Yang Jeongin 
- Siew Tser Ying
- Melody Leom
