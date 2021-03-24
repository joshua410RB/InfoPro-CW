module signal_path_nios_top_mod(

	//////////// CLOCK //////////
	input 		          		ADC_CLK_10,
	input 		          		MAX10_CLK1_50,
	input 		          		MAX10_CLK2_50,

	//////////// SDRAM //////////
	output		    [12:0]		DRAM_ADDR,
	output		     [1:0]		DRAM_BA,
	output		          		DRAM_CAS_N,
	output		          		DRAM_CKE,
	output		          		DRAM_CLK,
	output		          		DRAM_CS_N,
	inout 		    [15:0]		DRAM_DQ,
	output		          		DRAM_LDQM,
	output		          		DRAM_RAS_N,
	output		          		DRAM_UDQM,
	output		          		DRAM_WE_N,

	//////////// SEG7 //////////
	output		     [7:0]		HEX0,
	output		     [7:0]		HEX1,
	output		     [7:0]		HEX2,
	output		     [7:0]		HEX3,
	output		     [7:0]		HEX4,
	output		     [7:0]		HEX5,

	//////////// KEY //////////
	input 		     [1:0]		KEY,

	//////////// LED //////////
	output		     [9:0]		LEDR,

	//////////// SW //////////
	input 		     [9:0]		SW,

	//////////// VGA //////////
	output		     [3:0]		VGA_B,
	output		     [3:0]		VGA_G,
	output		          		VGA_HS,
	output		     [3:0]		VGA_R,
	output		          		VGA_VS,

	//////////// Accelerometer //////////
	output		          		GSENSOR_CS_N,
	input 		     [2:1]		GSENSOR_INT,
	output		          		GSENSOR_SCLK,
	inout 		          		GSENSOR_SDI,
	inout 		          		GSENSOR_SDO,

	//////////// Arduino //////////
	inout 		    [15:0]		ARDUINO_IO,
	inout 		          		ARDUINO_RESET_N,

	//////////// GPIO, GPIO connect to GPIO Default //////////
	inout 		    [35:0]		GPIO
);

    assign ARDUINO_IO[8] = ready;
    assign ARDUINO_IO[9] = data_interrupt;

    logic bus_clk;
    logic bus_sclk;
    logic sys_clk;
    logic mem_clk;
    logic pll_lock;

    logic[15:0] result;
	logic[15:0] x_out;
	logic[15:0] y_out;
    logic[15:0] x_read;
    logic[15:0] y_read;
    logic[15:0] z_read;
    logic ready;
    logic data_interrupt;
    logic[1:0] x_bank;
    logic[1:0] y_bank;
    logic[1:0] z_bank;

    logic[8:0] update_ctrl; // [8]update_en, [7:6]update_axis, [5:4]update_bank, [3:0]update_index
    logic update_en;
    logic[1:0] update_axis;
    logic[1:0] update_bank;
    logic[3:0] update_index;
    logic[15:0] update_value;

    logic[9:0] led;
	 
	assign HEX0[7] = 1;
 	assign HEX1[7] = 1;
	assign HEX2[7] = 1;
   	assign HEX3[7] = 1;
	assign HEX4 = 255;
	assign HEX5 = 255;

	hex_to_7seg disp0(HEX0, y_read[3:0]);
   	hex_to_7seg disp1(HEX1, y_read[7:4]);
	hex_to_7seg disp2(HEX2, y_read[11:8]);
	hex_to_7seg disp3(HEX3, y_read[15:12]);

    always_comb begin
		LEDR[1:0] = y_bank;
//        LEDR = led;
//
//        ARDUINO_IO[8] = ready;
//        ARDUINO_IO[9] = data_interrupt;
        result = x_read;

		x_read = x_out + 16'h8000;
		y_read = y_out + 16'h8000;

        update_en = update_ctrl[8];
        update_axis = update_ctrl[7:6];
        update_bank = update_ctrl[5:4];
        update_index = update_ctrl[3:0];
    end

//	);
	
	nios2_cpu u0 (
			.accel_interrupt_export                 (data_interrupt),				//                 accel_interrupt.export
			.accel_xdata_export                     (x_read),        				//                     accel_xdata.export
			.accel_ydata_export                     (y_read),       		   		//                     accel_ydata.export
			.accel_zdata_export                     (z_read),        				//                     accel_zdata.export
			.clk_clk                                (sys_clk),       				//                                clk.clk
			.led_export                             (led),           				//                             led.export
			.reset_reset_n                          (KEY[0]),        				//                          reset.reset_n
			.switch_export                          (SW),            				//                          switch.export
			.update_control_export                  (update_ctrl),   				//                  update_control.export
			.update_value_export                    (update_value),  				//                    update_value.export
			.x_coeff_bank_export                    (x_bank),        				//                    x_coeff_bank.export
			.y_coeff_bank_export                    (y_bank),        				//                    y_coeff_bank.export
			.z_coeff_bank_export                    (z_bank),        				//                    z_coeff_bank.export
			.hex0_export        							 (),        					//        hex0_external_connection.export
			.hex1_export        							 (),        					//        hex1_external_connection.export
			.hex2_export        							 (),          				//        hex2_external_connection.export
			.hex3_export        							 (),        					//        hex3_external_connection.export
			.hex4_export        							 (),        					//        hex4_external_connection.export
			.hex5_export        							 (),        					//        hex5_external_connection.export
			.key1_button_export 							 (KEY[1])  		
			// key1_button_external_connection.export
	);


    signal_path_16_tap sig_path(
        .sys_clk(sys_clk),
        .bus_clk(bus_clk),
        .pll_lock(pll_lock),
        .x_data(x_out),
        .y_data(y_out),
        .z_data(z_read),
        .available(ready),
        .data_interrupt(data_interrupt),
        .x_bank(x_bank),
        .y_bank(y_bank),
        .z_bank(z_bank),
        .update_en(update_en),
        .update_axis(update_axis),
        .update_bank(update_bank),
        .update_index(update_index),
        .update_value(update_value),
        .spi_sclk(GSENSOR_SCLK),
        .spi_mosi(GSENSOR_SDI),
        .spi_miso(GSENSOR_SDO),
        .spi_cs(GSENSOR_CS_N)
    );

    pll1	pll1_inst (
        .inclk0 ( MAX10_CLK1_50 ),
        .c0 ( bus_clk ),
        .c1 ( bus_sclk ),
        .c2 ( sys_clk ),
        .c3 ( mem_clk ),
        .locked ( pll_lock )
	);

endmodule