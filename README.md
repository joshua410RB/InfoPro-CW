# InfoPro-CW

## How to use
### Server Set Up

Our server implementation uses Docker to deploy. It will start the broker and run mqtt_server.py which is the server handler. We implemented it with TLS encryption using a self signed Certificate Authority cert. The same cert is also used in the local computer. If you would like to use the Encrypted Version, you will either have to create your own certificates or approach one of the team members to start our server. Else, run the unencrypted version.

To deploy the server, in your cloud instance, install Docker and run the following commands in the server folder:
- With Encryption
```
docker build . -t infopro_server:1.0 --file Dockerfile.
docker run --it --rm -p 0.0.0.0:32552:8883/tcp infopro_server:1.0
```
- Without Encryption
```
docker build . -t infopro_server:1.0 --file Dockerfile_NoEncrypt
docker run --it --rm -p 0.0.0.0:32552:1883/tcp infopro_server:1.0 
```
This will initialise the server database and start the server client. 

### FPGA Set Up
- The ```.sof``` and ```.elf``` files in the ```hardware/sof_elf``` folder can be used directly to blast and program the FPGA. 
- Blast the ```sof_elf/16_tap.sof``` into the FPGA using the 
- Use Nios2-download to download ```sof_elf/16_tap.elf``` software.
- Other working files are stored in ```hardware/quartus_files``` for reference.

### Client Set Up

- On your own local computer, do 

```
./launch_client.sh
```

This will start your ```nios2_command_shell``` that is necessary for uart communication

```main.py``` is then ran to start the game interface, the fpga uart script and the mqtt client.


## Testing
1. FPGA UART Connection Test
The ```local_computer/test_uart_handler.py``` script interfaces to the uart_handler function and requests certain actions from the user, subsequently verifying if the data is streamed correctly to the appropriate channels based on that. 
Before running this script, make sure that the FPGA has been set up and blasted with the necessary software.

2. Server Connection/Load Test
- The ```local_computer/test_client_server.py``` script is used to perform testing. To perform testing, run 
```
python3 local_computer/test_client_server.py --testno _testno_
```

_testno_ is used to specify the number of clients that will be simulated. 

In the script, based on the specified number of clients, 

## The Team
- Si Yu Tan
- Joshua Lim
- Zhao Siting
- Yang Jeongin 
- Siew Tser Ying
- Melody Leom
