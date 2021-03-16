#include <stdio.h>
#include <system.h>
#include "altera_avalon_pio_regs.h"
#include "sys/alt_irq.h"
#include <stdlib.h>

int x_data;
int y_data;
int z_data;

int lol;
int sw;
int xbank;
int ybank;
int zbank;

void readValues()	{
	x_data = IORD(ACCEL_XREAD_BASE,0);
	y_data = IORD(ACCEL_YREAD_BASE,0);
	z_data = IORD(ACCEL_ZREAD_BASE,0);
	IOWR_ALTERA_AVALON_PIO_EDGE_CAP(ACCEL_DATA_INTERRUPT_BASE, 0);
}

void IRQInit(void *isr)	{
	alt_irq_register(ACCEL_DATA_INTERRUPT_IRQ, 0, isr);
}

int main()
{
  printf("Hello from Nios II!\n");

  IRQInit(readValues);												// start interrupt handler for accelerometer values
  IOWR_ALTERA_AVALON_PIO_IRQ_MASK(ACCEL_DATA_INTERRUPT_BASE, 0xFF);

  while(1)	{
	  IOWR(PRINT0_BASE,0, x_data);
	  IOWR(PRINT1_BASE,0, y_data);

	  sw = IORD(SWITCH_BASE,0);
	  xbank = sw&3;							// SW1-0 selects x-axis coefficient bank
	  ybank = (sw>>2)&3;					// SW3-2 selects y-axis coefficient bank
	  zbank = (sw>>4)&3;					// SW5-4 selects z-axis coefficient bank
	  IOWR(X_COEFF_BANK_BASE, 0, xbank);	// set x-axis coefficient bank
	  IOWR(Y_COEFF_BANK_BASE, 0, ybank);	// set y-axis coefficient bank
	  IOWR(Z_COEFF_BANK_BASE, 0, zbank);

//	  printf("data: %d\n",lol);
  }

  return 0;
}
