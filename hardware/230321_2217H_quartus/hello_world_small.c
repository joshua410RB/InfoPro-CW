#include "system.h"
#include <stdlib.h>
#include <sys/alt_stdio.h>
#include <sys/alt_irq.h>
#include <unistd.h>
#include <sys/alt_alarm.h>
#include "altera_avalon_pio_regs.h"
#include "altera_avalon_timer_regs.h"
#include "altera_avalon_timer.h"
#include "altera_avalon_jtag_uart_regs.h"
#include "altera_avalon_jtag_uart.h"

volatile int update_flag;
volatile char recv_char;
volatile int rx_flag;

int x_data;
int y_data;
int z_data;

int lol;
int sw;
int xbank;
int ybank;
int zbank;

int button_datain;
int bomb_thrown = 0;

int counter1=0;

enum state {
	normal = 0,
	slow = 1,
	stop = 2,
};
alt_u8 mode = normal;

//=========== Functions for signal path interrupt handler ==========================
void readValues()	{					// ISR to store new values into variables
	x_data = IORD(ACCEL_XREAD_BASE,0);
	y_data = IORD(ACCEL_YREAD_BASE,0);
	z_data = IORD(ACCEL_ZREAD_BASE,0);
	IOWR_ALTERA_AVALON_PIO_EDGE_CAP(ACCEL_DATA_INTERRUPT_BASE, 0);	// clear interrupt edge capture register
	update_flag=1;
}

void IRQInit(void *isr)	{
	alt_irq_register(ACCEL_DATA_INTERRUPT_IRQ, 0, isr);	// register interrupt handler and ISR for fetching new values
}
//==================================================================================

//=========== Functions for JTAG UART interrupt handler ============================
void sys_jtag_isr()	{
	alt_u32 d=0;
	d = IORD_ALTERA_AVALON_JTAG_UART_DATA(JTAG_UART_BASE);
	char c = (char) (d & 0xFF);
	if(c!=10)	{
		recv_char = c;
		rx_flag=1;
	}
}

void jtag_uart_init(void *isr)	{
	IOWR_ALTERA_AVALON_JTAG_UART_CONTROL(JTAG_UART_BASE, 0x01);
	alt_irq_register(JTAG_UART_IRQ, 0, isr);
}
//==================================================================================

//=========== Functions for printing letters to 7-seg displays =====================
int getLetter(char letter){
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
        IOWR_ALTERA_AVALON_PIO_DATA(HEX5_BASE, getLetter(let5));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX4_BASE, getLetter(let4));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX3_BASE, getLetter(let3));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX2_BASE, getLetter(let2));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX1_BASE, getLetter(let1));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX_0_BASE, getLetter(let0));
		return;
}
//================================================================================


int main()
{
  //========== Initialize interrupt handlers =======================================
  IRQInit(readValues);												// start interrupt handler for accelerometer values
  IOWR_ALTERA_AVALON_PIO_IRQ_MASK(ACCEL_DATA_INTERRUPT_BASE, 0xFF);
  update_flag=0;
  counter1=0;
  jtag_uart_init(sys_jtag_isr);
  //================================================================================

  while(1)	{
	  button_datain = IORD_ALTERA_AVALON_PIO_DATA(KEY1_BUTTON_BASE); // button_datain = 1 if key1 is not pressed, pressing key1 sends button_datain = 0
	  sw = IORD(SWITCH_BASE,0);

	  if(update_flag==1)	{	// print accelerometer data
		  alt_printf("<->%x|%x|%x|%x<|> \n", x_data, y_data, z_data, bomb_thrown);
		  update_flag=0;
	  }

	  //===== uart code: handle incoming chars from local pc to change mode / increase bomb count ======
	  if(rx_flag==1)	{	// code for handling incoming messages
		  rx_flag=0;
		  switch (recv_char){
		  	case 'n':
		  		mode = normal;
		  		break;
		    case 's':
		    	mode = slow;
		    	break;
		    case 'x':
		    	mode = stop;
		        break;
		  }
	  }
	  //================================================================================================

	  //============ printing to 7-seg display: mode,  and throwing bombs ==============================
		if(button_datain == 0 && counter1==0)	{
			counter1=1;
		}
		if(counter1>0)	{
			print_letters('T', 'H', 'R', 'O', 'V', 'V');
			bomb_thrown = 1;
		}
		else	{
			if (mode == stop){
				print_letters('S', 'T', 'O', 'P', '!', '!');
				bomb_thrown = 0;
		  	} 
		  	else if (mode == slow){
				print_letters('S', 'L', 'O', 'U', 'U', '!');
				bomb_thrown = 0;
		  	} 
			else {
				print_letters('N', 'O', 'R', 'M', 'A', 'L' );
				bomb_thrown = 0;
		  	}
		}
		if(counter1>0)	{
			if(counter1 > 60000)	{
				counter1=0;
			}
			else	{
				counter1++;
			}
		}
	  //================================================================================================

	  //================== setting filter coefficients based on the mode player is in ==================
	  if (mode == normal){
		  xbank = 0;
		  ybank = 0;
		  zbank = 0;
	  } else if (mode == slow){
		  xbank = 1;
		  ybank = 1;
		  zbank = 1;
	  } else if (mode == stop){
		  xbank = 3;
		  ybank = 3;
		  zbank = 3;
	  }
	  IOWR(X_COEFF_BANK_BASE, 0, xbank);	// set x-axis coefficient bank
	  IOWR(Y_COEFF_BANK_BASE, 0, ybank);	// set y-axis coefficient bank
	  IOWR(Z_COEFF_BANK_BASE, 0, zbank);	// set z-axis coefficient bank
	  //==================== coeffs are set in signal_path_32_tap.v ===================================
  }

  return 0;
}
