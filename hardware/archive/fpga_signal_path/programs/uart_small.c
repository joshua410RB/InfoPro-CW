//#include <stdio.h>
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

int data=8;
volatile char recv_char;
int sw;
int rx_flag=0;

char *wtf;

int acc=0;

void sys_jtag_isr()	{
	alt_u32 d=0;
	d = IORD_ALTERA_AVALON_JTAG_UART_DATA(JTAG_UART_BASE);
	char c = (char) (d & 0xFF);
	if(c!=10)	{
		switch(c)	{
		case 'f':
			data = 2;
			break;
		case 'o':
			data=5;
			break;
		}
		recv_char = c;
		rx_flag=1;
	//	recv_char = alt_getchar();
	//	*wtf = recv_char;
//		alt_printf("data: %c\n",recv_char);
	}
}

void jtag_uart_init(void *isr)	{
	IOWR_ALTERA_AVALON_JTAG_UART_CONTROL(JTAG_UART_BASE, 0x01);
	alt_irq_register(JTAG_UART_IRQ, 0, isr);
}

int main()
{
	IOWR(LED_BASE, 0, 3);
	alt_printf("Hello from Nios II!\n");

	jtag_uart_init(sys_jtag_isr);

	IOWR(PRINT0_BASE, 0, data);
	alt_printf("heyyo\n");

  while(1)	{
	  if(rx_flag==1)	{
		  acc++;
		  IOWR(PRINT1_BASE, 0, acc);
//		  alt_printf("data: %x\n",recv_char);
		  alt_printf("<--->%c<|-|>", recv_char);
		  rx_flag=0;
	  }

	  IOWR(PRINT0_BASE, 0, data);
	  sw = IORD(SWITCH_BASE,0);
	  IOWR(LED_BASE, 0, sw);
  }

  return 0;
}
