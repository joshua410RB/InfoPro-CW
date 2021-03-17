#!/bin/bash
SCRIPT="nios2-download -g /mnt/c/Users/tansi/Documents/Imperial_College_London/Info_Processing/InfoPro-CW/local_computer/test_fpga_software.elf;"
# Activate nios2 command shell
/mnt/c/intelFPGA_lite/20.1.1/nios2eds/nios2_command_shell.sh ${SCRIPT}

# Download nios2 software
# nios2-download -g test_fpga_software.elf