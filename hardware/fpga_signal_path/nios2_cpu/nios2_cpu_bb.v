
module nios2_cpu (
	accel_interrupt_export,
	accel_xdata_export,
	accel_ydata_export,
	accel_zdata_export,
	clk_clk,
	disp0_export,
	disp1_export,
	led_export,
	reset_reset_n,
	switch_export,
	update_control_export,
	update_value_export,
	x_coeff_bank_export,
	y_coeff_bank_export,
	z_coeff_bank_export);	

	input		accel_interrupt_export;
	input	[15:0]	accel_xdata_export;
	input	[15:0]	accel_ydata_export;
	input	[15:0]	accel_zdata_export;
	input		clk_clk;
	output	[7:0]	disp0_export;
	output	[7:0]	disp1_export;
	output	[9:0]	led_export;
	input		reset_reset_n;
	input	[10:0]	switch_export;
	output	[8:0]	update_control_export;
	output	[15:0]	update_value_export;
	output	[1:0]	x_coeff_bank_export;
	output	[1:0]	y_coeff_bank_export;
	output	[1:0]	z_coeff_bank_export;
endmodule
