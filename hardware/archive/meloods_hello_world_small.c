#include "system.h"
#include <sys/alt_stdio.h> // alt_printf
#include <stdio.h>
#include <unistd.h> // usleep from newlib
#include <sys/alt_alarm.h>
#include <stdlib.h>

#include "altera_up_avalon_accelerometer_spi.h"
#include "altera_avalon_timer_regs.h"
#include "altera_avalon_timer.h"
#include "altera_avalon_pio_regs.h"
#include "sys/alt_irq.h"
#include "altera_avalon_jtag_uart_regs.h"
#include "altera_avalon_jtag_uart.h"

#define OFFSET -32
#define PWM_PERIOD 16

// Global Variables
alt_8 pwm = 0;
alt_u8 led;
int level;
alt_16 coeff[] = {0x3333, 0x3333, 0x3333, 0x3333, 0x3333};
#define coeff_len (sizeof(coeff)/sizeof(coeff[0]))
alt_32 memory[coeff_len];
int bomb_count=0;

// Enums
enum state {
	normal = 0,
	slow = 1,
	stop = 2,
};
alt_u8 mode = normal;

// moving average filter - change to lowpass?
float fir_filter(alt_32 acc_read){
	alt_32 output = 0;
	alt_32 current = acc_read;
	for (int i = 0; i <coeff_len; i++){
		output += coeff[i] * memory[i];
	}
	output = output >> 16;
	for (int i = 0; i < coeff_len - 1; i++){
		memory[i] = memory[i + 1];
	}
	memory[coeff_len - 1] = acc_read;
	return output;
}

// print filter coefficients out
void print_filter(){
	for (int i = 0; i <coeff_len; i++){
		printf("Coeff %d: %d ", i, coeff[i]);
	}
	alt_printf("\n");
}

void change_filter_mode (int state) {
	switch (state){
	    case 's': //slow:
	    	for (int i=0; i<5; i++) {
	    		coeff[i] = 0x1999;
	    	}
	    	break;
	    case 'x': //stop
	    	for (int i=0; i<5; i++) {
	    		coeff[i] = 0;
	    	}
	    	break;
	}
	return;
}


void led_write(alt_u8 led_pattern) {
    IOWR(LED_BASE, 0, led_pattern);
}
// function to light up the LED lights according to x_read
void convert_read(alt_32 acc_read, int * level, alt_u8 * led) {
    acc_read += OFFSET;
    alt_u8 val = (acc_read >> 6) & 0x07;
    * led = (8 >> val) | (8 << (8 - val));
    * level = (acc_read >> 1) & 0x1f;
}

//Handle Interrupt
void sys_timer_isr() {
    IOWR_ALTERA_AVALON_TIMER_STATUS(TIMER_BASE, 0);
    if (pwm < abs(level)) {
        if (level < 0) {
            led_write(led << 1);
        } else {
            led_write(led >> 1);
        }
    } else {
        led_write(led);
    }
    if (pwm > PWM_PERIOD) {
        pwm = 0;
    } else {
        pwm++;
    }
}

//Interrupt
void timer_init(void * isr) {
    IOWR_ALTERA_AVALON_TIMER_CONTROL(TIMER_BASE, 0x0003);
    IOWR_ALTERA_AVALON_TIMER_STATUS(TIMER_BASE, 0);
    IOWR_ALTERA_AVALON_TIMER_PERIODL(TIMER_BASE, 0x0900);
    IOWR_ALTERA_AVALON_TIMER_PERIODH(TIMER_BASE, 0x0000);
    alt_irq_register(TIMER_IRQ, 0, isr);
    IOWR_ALTERA_AVALON_TIMER_CONTROL(TIMER_BASE, 0x0007);
}

void sys_jtag_isr() {
    alt_u32 data = IORD_ALTERA_AVALON_JTAG_UART_DATA(JTAG_UART_BASE);
    char tmp = (char) (data & 0xFF);
    switch (tmp){
    // normal mode
    case 'n':
    	mode = normal;
    	break;
    // slow mode, when player has been bombed
    case 's':
    	mode = slow;
    	break;
    // stopped mode, when player has ran into obstacle?
    case 'x':
    	mode = stop;
    	break;
    // whenever player picks up a bomb, print out to terminal and 7-seg display to indicate so
    case 'b':
    	bomb_count++;
    	printf ("bomb_count: %d \n", bomb_count);
    	switch (bomb_count){
    	case 1:
    		for (int i=0; i<60000; i++) {print_letters('B', 'O', 'N', 'B', '.', '1');}
    		break;
    	case 2:
    	    for (int i=0; i<60000; i++) {print_letters('B', 'O', 'N', 'B', '.', '2');}
    	    break;
    	case 3:
    	    for (int i=0; i<60000; i++) {print_letters('B', 'O', 'N', 'B', '.', '3');}
    	    break;
    	case 4:
    	    for (int i=0; i<60000; i++) {print_letters('B', 'O', 'N', 'B', '.', '4');}
    	    break;
    	case 5:
    	    for (int i=0; i<60000; i++) {print_letters('B', 'O', 'N', 'B', '.', '5');}
    	    break;
    	case 6:
    	    for (int i=0; i<60000; i++) {print_letters('B', 'O', 'N', 'B', '.', '6');}
    	    break;
    	case 7:
    	    for (int i=0; i<60000; i++) {print_letters('B', 'O', 'N', 'B', '.', '6');}
    	    break;
    	case 8:
    	    for (int i=0; i<60000; i++) {print_letters('B', 'O', 'N', 'B', '.', '8');}
    	    break;
    	case 9:
    	    for (int i=0; i<60000; i++) {print_letters('B', 'O', 'N', 'B', '.', '9');}
    	    break;
    	}
    	break;
    }
}

void jtag_uart_init(void * isr){
	// Enable JTAG IRQ
	IOWR_ALTERA_AVALON_JTAG_UART_CONTROL(JTAG_UART_BASE, 0x01);
	// Enable Interrupt Service
	alt_irq_register(JTAG_UART_IRQ, 0, isr);
}

// getBin and printLetters are used to print to 7-seg displays
int getBin(char letter){
	switch(letter){
	case '0':
		return 0b1000000;
	case '1':
		return 0b1111001;
	case '2':
		return 0b0100100;
	case '3':
		return 0b0110000;
	case '4':
		return 0b0011001;
	case '5':
		return 0b0010010;
	case '6':
		return 0b0000010;
	case '7':
		return 0b1111000;
	case '8':
		return 0b0000000;
	case '9':
		return 0b0010000;
	case 'A':
		return 0b0001000;
	case 'B'://Lowercase
		return 0b0000011;
	case 'C':
		return 0b1000110;
	case 'D'://Lowercase
		return 0b0100001;
	case 'E':
		return 0b0000110;
	case 'F':
		return 0b0001110;
	case 'G':
		return 0b0010000;
	case 'H':
		return 0b0001001;
	case 'I':
		return 0b1111001;
	case 'J':
		return 0b1110001;
	case 'K':
		return 0b0001010;
	case 'L':
		return 0b1000111;
	case 'N':
		return 0b0101011;
	case 'O':
		return 0b1000000;
	case 'P':
		return 0b0001100;
	case 'Q':
		return 0b0011000;
	case 'R'://Lowercase
		return 0b0101111;
	case 'S':
		return 0b0010010;
	case 'T':
		return 0b0000111;
	case 'U':
		return 0b1000001;
	case 'V':
		return 0b1100011;
	case 'X':
		return 0b0011011;
	case 'Y':
		return 0b0010001;
	case 'Z':
		return 0b0100100;
	default:
		return 0b1111111;
	}
}
void print_letters(char let5, char let4, char let3, char let2, char let1, char let0){
        IOWR_ALTERA_AVALON_PIO_DATA(HEX5_BASE, getBin(let5));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX4_BASE, getBin(let4));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX3_BASE, getBin(let3));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX2_BASE, getBin(let2));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX1_BASE, getBin(let1));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX0_BASE, getBin(let0));
		return;
}

int main() {
//	alt_u32 start, end, total_time;
    alt_32 x_read, x_filtered, y_read, y_filtered;
    alt_up_accelerometer_spi_dev * acc_dev;
    int button_datain;

    acc_dev = alt_up_accelerometer_spi_open_dev("/dev/accelerometer_spi");
    if (acc_dev == NULL) { // if return 1, check if the spi ip name is "accelerometer_spi"
        return 1;
    }

    timer_init(sys_timer_isr);
    jtag_uart_init(sys_jtag_isr);
    alt_printf("Press n for n mode\n");
    alt_printf("Press s for slow mode\n");
    alt_printf("Press x for stop mode\n");
    alt_printf("Press b to get bomb\n");

	while (1) {
		alt_up_accelerometer_spi_read_x_axis(acc_dev, & x_read);
		alt_up_accelerometer_spi_read_y_axis(acc_dev, & y_read);

		//button_datain = 3 if both buttons are NOT pressed
		//button_datain = 2 if only key0 (upper) button is pressed
		//button_datain = 1 if only key1 (lower) button is pressed
		button_datain = IORD_ALTERA_AVALON_PIO_DATA(BUTTON_BASE);

		if (bomb_count==0) {
			if (mode == stop) {
				print_letters('S', 'T', 'O', 'P', '!', '!');
				change_filter_mode('x');
				x_filtered = fir_filter(x_read);
				y_filtered = fir_filter(y_read);
				convert_read(x_filtered, & level, & led);
//				printf("x_raw: %d, x_filtered:%d \n", x_read, x_filtered);
//				printf("y_raw: %d, y_filtered:%d \n", y_read, y_filtered);
			} else if (mode == slow) {
				print_letters('S', 'L', 'O', 'U', 'U', '!');
				change_filter_mode('s');
				x_filtered = fir_filter(x_read);
				y_filtered = fir_filter(y_read);
				convert_read(x_filtered, & level, & led);
//				printf("x_raw: %d, x_filtered:%d \n", x_read, x_filtered);
//				printf("y_raw: %d, y_filtered:%d \n", y_read, y_filtered);
			} else {
				print_letters('N', 'O', 'R', 'M', 'A', 'L' );
				x_filtered = fir_filter(x_read);
				y_filtered = fir_filter(y_read);
				convert_read(x_filtered, & level, & led);
//				printf("x_raw: %d, x_filtered:%d \n", x_read, x_filtered);
//				printf("y_raw: %d, y_filtered:%d \n", y_read, y_filtered);
			}
		}
		// player has bombs - press key1 button to throw a bomb
		else {
			if (button_datain == 1) {
				for (int i=0; i<60000; i++) {print_letters('T', 'H', 'R', 'O', 'V', 'V');}
				bomb_count--;
				printf ("Bomb has been thrown! \n");
				printf ("bomb_count: %d \n", bomb_count);
				bomb_throw = 1;
			}
			else if (button_datain == 3 && mode == stop) {
				print_letters('S', 'T', 'O', 'P', '!', '!');
				change_filter_mode('x');
				x_filtered = fir_filter(x_read);
				y_filtered = fir_filter(y_read);
				convert_read(x_filtered, & level, & led);
//				printf("x_raw: %d, x_filtered:%d \n", x_read, x_filtered);
//				printf("y_raw: %d, y_filtered:%d \n", y_read, y_filtered);
			} else if (button_datain == 3 && mode == slow) {
				print_letters('S', 'L', 'O', 'U', 'U', '!');
				change_filter_mode('s');
				x_filtered = fir_filter(x_read);
				y_filtered = fir_filter(y_read);
				convert_read(x_filtered, & level, & led);
//				printf("x_raw: %d, x_filtered:%d \n", x_read, x_filtered);
//				printf("y_raw: %d, y_filtered:%d \n", y_read, y_filtered);
			} else {
				print_letters('N', 'O', 'R', 'M', 'A', 'L' );
				convert_read(x_read, & level, & led);
				x_filtered = fir_filter(x_read);
				y_filtered = fir_filter(y_read);
				convert_read(x_read, & level, & led);
//				printf("x_raw: %d, x_filtered:%d \n", x_read, x_filtered);
//				printf("y_raw: %d, y_filtered:%d \n", y_read, y_filtered);
			}
		}
	}
}
