# FPGA Signal Path
Hardware implementation of the signal path (Accelerometer read + FIR filter). Reads each of the 3 axes and applies and 16-tap FIR filter to the data. Each axis has its own dedicated FIR filter. 

The signal path module handles updating the filter at the prescribed sample rate, freeing the NIOS2 to do other things. An interrupt is used to signal to the NIOS2 that new values are available (implementation example in "accel_test.c" under "programs" folder)

Sample Rate: 100Hz
Number of Taps: 16

The output of each filter is a 16-bit signed 2s-complement integer. They are automatically saved into designated variables in the sample program

Each filter has 4 dedicated banks of coefficients that can be used to rapidly change filter characteristics on the fly (as opposed to writing each tap coefficient manually with a NIOS2). The banks are independent for each filter allowing different sets of coefficents to be pre-loaded for each axis. The coefficients can also be individually edited from the NIOS2 (sample code to come)

Selecting the coefficient bank to use is done through a 2-wire bus

The default coefficients can be edited in "signal_path_16_tap.v" (scroll down to where x,y,z coefficients are initialised)
</br>

## Building the project
The module "signal_path_nios_top_mod.v" contains an instance of the signal path and a NIOS2 core. Build the project and the flash the FPGA with the corresponding .sof file, then build the code for the system

</br>

## Developing Code
1. Create a NIOS2 project in eclipse from the "Hello_World" template (do not use hello_world_small)
2. Copy the code from "programs/accel_test.c" and run it
3. x-axis data is diaplyed on HEX5-4 and y-axis data on HEX1-0. SW1-0 select the x-axis filter coefficient bank and SW3-2 select the y-axis filter coefficient bank

Note: When displaying values on the 7seg displays, the NIOS2 stores the value to a PIO register. The decoding is handled in hardware by dedicated hex_to_7seg modules
</br>

## Coefficients
The coefficients are quantized 16-bit decimal numbers. Quantization is done by shifting the fixed-point binary form of the decimal left by 16 bits. 

For example (using 4-bits): 0.5 in fixed point binary is 0.1000, its quantized form is 1000 (shoft left by 4-bits)