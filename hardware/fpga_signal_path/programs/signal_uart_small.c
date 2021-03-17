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

int main()
{
  //========== Initialize interrupt handlers =======================================
  IRQInit(readValues);												// start interrupt handler for accelerometer values
  IOWR_ALTERA_AVALON_PIO_IRQ_MASK(ACCEL_DATA_INTERRUPT_BASE, 0xFF);
  update_flag=0;
  jtag_uart_init(sys_jtag_isr);
  //================================================================================

  while(1)	{
	  sw = IORD(SWITCH_BASE,0);
	  if(update_flag==1)	{	// print accelerometer data
//		  alt_printf("<->");
		  alt_printf("<->%x|%x|%x|%x<|>", x_data, y_data, z_data, sw);
//		  alt_printf("<|>");
		  update_flag=0;
	  }

	  if(rx_flag==1)	{	// code for handling incoming messages
		  rx_flag=0;
		  IOWR(PRINT0_BASE, 0, recv_char);
	  }

//	  IOWR(PRINT0_BASE,0, x_data);	// print x-axis data to HEX 1-0
	  IOWR(PRINT1_BASE,0, y_data);	// print y-axis data to HEX 5-4

	  xbank = sw&3;							// SW1-0 selects x-axis coefficient bank
	  ybank = (sw>>2)&3;					// SW3-2 selects y-axis coefficient bank
	  zbank = (sw>>4)&3;					// SW5-4 selects z-axis coefficient bank
	  IOWR(X_COEFF_BANK_BASE, 0, xbank);	// set x-axis coefficient bank
	  IOWR(Y_COEFF_BANK_BASE, 0, ybank);	// set y-axis coefficient bank
	  IOWR(Z_COEFF_BANK_BASE, 0, zbank);

  }

  return 0;
}
