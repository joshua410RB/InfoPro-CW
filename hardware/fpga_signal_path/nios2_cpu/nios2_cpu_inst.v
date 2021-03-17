	nios2_cpu u0 (
		.accel_interrupt_export (<connected-to-accel_interrupt_export>), // accel_interrupt.export
		.accel_xdata_export     (<connected-to-accel_xdata_export>),     //     accel_xdata.export
		.accel_ydata_export     (<connected-to-accel_ydata_export>),     //     accel_ydata.export
		.accel_zdata_export     (<connected-to-accel_zdata_export>),     //     accel_zdata.export
		.clk_clk                (<connected-to-clk_clk>),                //             clk.clk
		.disp0_export           (<connected-to-disp0_export>),           //           disp0.export
		.disp1_export           (<connected-to-disp1_export>),           //           disp1.export
		.led_export             (<connected-to-led_export>),             //             led.export
		.reset_reset_n          (<connected-to-reset_reset_n>),          //           reset.reset_n
		.switch_export          (<connected-to-switch_export>),          //          switch.export
		.update_control_export  (<connected-to-update_control_export>),  //  update_control.export
		.update_value_export    (<connected-to-update_value_export>),    //    update_value.export
		.x_coeff_bank_export    (<connected-to-x_coeff_bank_export>),    //    x_coeff_bank.export
		.y_coeff_bank_export    (<connected-to-y_coeff_bank_export>),    //    y_coeff_bank.export
		.z_coeff_bank_export    (<connected-to-z_coeff_bank_export>)     //    z_coeff_bank.export
	);

