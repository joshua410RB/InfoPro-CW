module signal_path_32_tap(
    input logic sys_clk,
    input logic bus_clk,
    input logic pll_lock,
    output logic[15:0] x_data,
    output logic[15:0] y_data,
    output logic[15:0] z_data,
    output logic available,
    output logic data_interrupt,

    input logic[1:0] x_bank,
    input logic[1:0] y_bank,
    input logic[1:0] z_bank,

    input logic update_en,
    input logic[1:0] update_axis,   // 0: disable, 1: x-axis, 2: y-axis, 3: z-axis
    input logic[1:0] update_bank,
    input logic[4:0] update_index,
    input logic[15:0] update_value,

    output logic spi_sclk,
    output logic spi_mosi,
    input logic spi_miso,
    output logic spi_cs
);
    parameter CLOCK_DIV = 500000 - 1;   // originally 500000

    typedef enum logic[3:0] {
        IDLE = 4'd0,
        ADDRESS_SETUP = 4'd1,
        ADDRESS = 4'd2,
        READ_SETUP = 4'd3,
        READ = 4'd4,
        HOLD = 4'd5,
        FILTER_SETUP = 4'd6,
        FILTER = 4'd7
    } state_t;

    logic[3:0] state;
    logic ir_reg;
    logic[31:0] timer_acc;
    wire[31:0] new_timer_acc;
    assign new_timer_acc = timer_acc + 1;

    logic accel_enable;
    logic accel_busy;
    logic accel_ready;

    logic fir_enable;
    logic fir_x_busy;
    logic fir_y_busy;
    logic fir_z_busy;

    logic[15:0] x;
    logic[15:0] y;
    logic[15:0] z;

    logic[15:0] xc[3:0][31:0];  // x coefficients (4 banks of 16 values each)
    logic[15:0] yc[3:0][31:0];  // y coefficients
    logic[15:0] zc[3:0][31:0];  // z coefficients

    initial begin   // initialise x coefficients
        xc[0][0] =  16'h1000;   // set 0
        xc[0][1] =  16'h1000;
        xc[0][2] =  16'h1000;
        xc[0][3] =  16'h1000;
        xc[0][4] =  16'h1000;
        xc[0][5] =  16'h1000;
        xc[0][6] =  16'h1000;
        xc[0][7] =  16'h1000;
        xc[0][8] =  16'h1000;
        xc[0][9] =  16'h1000;
        xc[0][10] = 16'h1000;
        xc[0][11] = 16'h1000;
        xc[0][12] = 16'h1000;
        xc[0][13] = 16'h1000;
        xc[0][14] = 16'h1000;
        xc[0][15] = 16'h1000;
        xc[0][16] = 16'h0000;
        xc[0][17] = 16'h0000;
        xc[0][18] = 16'h0000;
        xc[0][19] = 16'h0000;
        xc[0][20] = 16'h0000;
        xc[0][21] = 16'h0000;
        xc[0][22] = 16'h0000;
        xc[0][23] = 16'h0000;
        xc[0][24] = 16'h0000;
        xc[0][25] = 16'h0000;
        xc[0][26] = 16'h0000;
        xc[0][27] = 16'h0000;
        xc[0][28] = 16'h0000;
        xc[0][29] = 16'h0000;
        xc[0][30] = 16'h0000;
        xc[0][31] = 16'h0000;

        xc[1][0] =  16'h0800;   // set 1
        xc[1][1] =  16'h0800;
        xc[1][2] =  16'h0800;
        xc[1][3] =  16'h0800;
        xc[1][4] =  16'h0800;
        xc[1][5] =  16'h0800;
        xc[1][6] =  16'h0800;
        xc[1][7] =  16'h0800;
        xc[1][8] =  16'h0800;
        xc[1][9] =  16'h0800;
        xc[1][10] = 16'h0800;
        xc[1][11] = 16'h0800;
        xc[1][12] = 16'h0800;
        xc[1][13] = 16'h0800;
        xc[1][14] = 16'h0800;
        xc[1][15] = 16'h0800;
        xc[1][16] = 16'h0800;
        xc[1][17] = 16'h0800;
        xc[1][18] = 16'h0800;
        xc[1][19] = 16'h0800;
        xc[1][20] = 16'h0800;
        xc[1][21] = 16'h0800;
        xc[1][22] = 16'h0800;
        xc[1][23] = 16'h0800;
        xc[1][24] = 16'h0800;
        xc[1][25] = 16'h0800;
        xc[1][26] = 16'h0800;
        xc[1][27] = 16'h0800;
        xc[1][28] = 16'h0800;
        xc[1][29] = 16'h0800;
        xc[1][30] = 16'h0800;
        xc[1][31] = 16'h0800;

		xc[2][0] =  16'hFFFE;   // set 2
        xc[2][1] =  16'hFFF6;
        xc[2][2] =  16'hFFDC;
        xc[2][3] =  16'hFF9E;
        xc[2][4] =  16'hFF2A;
        xc[2][5] =  16'hFE82;
        xc[2][6] =  16'hFDCD;
        xc[2][7] =  16'hFD70;
        xc[2][8] =  16'hFE07;
        xc[2][9] =  16'h0044;
        xc[2][10] = 16'h04AE;
        xc[2][11] = 16'h0B4E;
        xc[2][12] = 16'h1380;
        xc[2][13] = 16'h1BF4;
        xc[2][14] = 16'h22F7;
        xc[2][15] = 16'h26F2;
        xc[2][16] = 16'h26F2;
        xc[2][17] = 16'h22F7;
        xc[2][18] = 16'h1BF4;
        xc[2][19] = 16'h1380;
        xc[2][20] = 16'h0B4E;
        xc[2][21] = 16'h04AE;
        xc[2][22] = 16'h0044;
        xc[2][23] = 16'hFE07;
        xc[2][24] = 16'hFD70;
        xc[2][25] = 16'hFDCD;
        xc[2][26] = 16'hFE82;
        xc[2][27] = 16'hFF2A;
        xc[2][28] = 16'hFF9E;
        xc[2][29] = 16'hFFDC;
        xc[2][30] = 16'hFFF6;
        xc[2][31] = 16'hFFFE;

        xc[3][0] =  16'h0000;   // set 3
        xc[3][1] =  16'h0000;
        xc[3][2] =  16'h0000;
        xc[3][3] =  16'h0000;
        xc[3][4] =  16'h0000;
        xc[3][5] =  16'h0000;
        xc[3][6] =  16'h0000;
        xc[3][7] =  16'h0000;
        xc[3][8] =  16'h0000;
        xc[3][9] =  16'h0000;
        xc[3][10] = 16'h0000;
        xc[3][11] = 16'h0000;
        xc[3][12] = 16'h0000;
        xc[3][13] = 16'h0000;
        xc[3][14] = 16'h0000;
        xc[3][15] = 16'h0000;
        xc[3][16] = 16'h0000;
        xc[3][17] = 16'h0000;
        xc[3][18] = 16'h0000;
        xc[3][19] = 16'h0000;
        xc[3][20] = 16'h0000;
        xc[3][21] = 16'h0000;
        xc[3][22] = 16'h0000;
        xc[3][23] = 16'h0000;
        xc[3][24] = 16'h0000;
        xc[3][25] = 16'h0000;
        xc[3][26] = 16'h0000;
        xc[3][27] = 16'h0000;
        xc[3][28] = 16'h0000;
        xc[3][29] = 16'h0000;
        xc[3][30] = 16'h0000;
        xc[3][31] = 16'h0000;
    end

    initial begin   // initialise y coefficients
        yc[0][0] =  16'h1000;   // set 0
        yc[0][1] =  16'h1000;
        yc[0][2] =  16'h1000;
        yc[0][3] =  16'h1000;
        yc[0][4] =  16'h1000;
        yc[0][5] =  16'h1000;
        yc[0][6] =  16'h1000;
        yc[0][7] =  16'h1000;
        yc[0][8] =  16'h1000;
        yc[0][9] =  16'h1000;
        yc[0][10] = 16'h1000;
        yc[0][11] = 16'h1000;
        yc[0][12] = 16'h1000;
        yc[0][13] = 16'h1000;
        yc[0][14] = 16'h1000;
        yc[0][15] = 16'h1000;
        yc[0][16] = 16'h0000;
        yc[0][17] = 16'h0000;
        yc[0][18] = 16'h0000;
        yc[0][19] = 16'h0000;
        yc[0][20] = 16'h0000;
        yc[0][21] = 16'h0000;
        yc[0][22] = 16'h0000;
        yc[0][23] = 16'h0000;
        yc[0][24] = 16'h0000;
        yc[0][25] = 16'h0000;
        yc[0][26] = 16'h0000;
        yc[0][27] = 16'h0000;
        yc[0][28] = 16'h0000;
        yc[0][29] = 16'h0000;
        yc[0][30] = 16'h0000;
        yc[0][31] = 16'h0000;

        yc[1][0] =  16'h0800;   // set 1
        yc[1][1] =  16'h0800;
        yc[1][2] =  16'h0800;
        yc[1][3] =  16'h0800;
        yc[1][4] =  16'h0800;
        yc[1][5] =  16'h0800;
        yc[1][6] =  16'h0800;
        yc[1][7] =  16'h0800;
        yc[1][8] =  16'h0800;
        yc[1][9] =  16'h0800;
        yc[1][10] = 16'h0800;
        yc[1][11] = 16'h0800;
        yc[1][12] = 16'h0800;
        yc[1][13] = 16'h0800;
        yc[1][14] = 16'h0800;
        yc[1][15] = 16'h0800;
        yc[1][16] = 16'h0800;
        yc[1][17] = 16'h0800;
        yc[1][18] = 16'h0800;
        yc[1][19] = 16'h0800;
        yc[1][20] = 16'h0800;
        yc[1][21] = 16'h0800;
        yc[1][22] = 16'h0800;
        yc[1][23] = 16'h0800;
        yc[1][24] = 16'h0800;
        yc[1][25] = 16'h0800;
        yc[1][26] = 16'h0800;
        yc[1][27] = 16'h0800;
        yc[1][28] = 16'h0800;
        yc[1][29] = 16'h0800;
        yc[1][30] = 16'h0800;
        yc[1][31] = 16'h0800;

		yc[2][0] =  16'hFFFE;   // set 2
        yc[2][1] =  16'hFFF6;
        yc[2][2] =  16'hFFDC;
        yc[2][3] =  16'hFF9E;
        yc[2][4] =  16'hFF2A;
        yc[2][5] =  16'hFE82;
        yc[2][6] =  16'hFDCD;
        yc[2][7] =  16'hFD70;
        yc[2][8] =  16'hFE07;
        yc[2][9] =  16'h0044;
        yc[2][10] = 16'h04AE;
        yc[2][11] = 16'h0B4E;
        yc[2][12] = 16'h1380;
        yc[2][13] = 16'h1BF4;
        yc[2][14] = 16'h22F7;
        yc[2][15] = 16'h26F2;
        yc[2][16] = 16'h26F2;
        yc[2][17] = 16'h22F7;
        yc[2][18] = 16'h1BF4;
        yc[2][19] = 16'h1380;
        yc[2][20] = 16'h0B4E;
        yc[2][21] = 16'h04AE;
        yc[2][22] = 16'h0044;
        yc[2][23] = 16'hFE07;
        yc[2][24] = 16'hFD70;
        yc[2][25] = 16'hFDCD;
        yc[2][26] = 16'hFE82;
        yc[2][27] = 16'hFF2A;
        yc[2][28] = 16'hFF9E;
        yc[2][29] = 16'hFFDC;
        yc[2][30] = 16'hFFF6;
        yc[2][31] = 16'hFFFE;

        yc[3][0] =  16'h0000;   // set 3
        yc[3][1] =  16'h0000;
        yc[3][2] =  16'h0000;
        yc[3][3] =  16'h0000;
        yc[3][4] =  16'h0000;
        yc[3][5] =  16'h0000;
        yc[3][6] =  16'h0000;
        yc[3][7] =  16'h0000;
        yc[3][8] =  16'h0000;
        yc[3][9] =  16'h0000;
        yc[3][10] = 16'h0000;
        yc[3][11] = 16'h0000;
        yc[3][12] = 16'h0000;
        yc[3][13] = 16'h0000;
        yc[3][14] = 16'h0000;
        yc[3][15] = 16'h0000;
        yc[3][16] = 16'h0000;
        yc[3][17] = 16'h0000;
        yc[3][18] = 16'h0000;
        yc[3][19] = 16'h0000;
        yc[3][20] = 16'h0000;
        yc[3][21] = 16'h0000;
        yc[3][22] = 16'h0000;
        yc[3][23] = 16'h0000;
        yc[3][24] = 16'h0000;
        yc[3][25] = 16'h0000;
        yc[3][26] = 16'h0000;
        yc[3][27] = 16'h0000;
        yc[3][28] = 16'h0000;
        yc[3][29] = 16'h0000;
        yc[3][30] = 16'h0000;
        yc[3][31] = 16'h0000;
    end

    initial begin   // initialise z coefficients
        zc[0][0] =  16'h1000;   // set 0
        zc[0][1] =  16'h1000;
        zc[0][2] =  16'h1000;
        zc[0][3] =  16'h1000;
        zc[0][4] =  16'h1000;
        zc[0][5] =  16'h1000;
        zc[0][6] =  16'h1000;
        zc[0][7] =  16'h1000;
        zc[0][8] =  16'h1000;
        zc[0][9] =  16'h1000;
        zc[0][10] = 16'h1000;
        zc[0][11] = 16'h1000;
        zc[0][12] = 16'h1000;
        zc[0][13] = 16'h1000;
        zc[0][14] = 16'h1000;
        zc[0][15] = 16'h1000;
        zc[0][16] = 16'h0000;
        zc[0][17] = 16'h0000;
        zc[0][18] = 16'h0000;
        zc[0][19] = 16'h0000;
        zc[0][20] = 16'h0000;
        zc[0][21] = 16'h0000;
        zc[0][22] = 16'h0000;
        zc[0][23] = 16'h0000;
        zc[0][24] = 16'h0000;
        zc[0][25] = 16'h0000;
        zc[0][26] = 16'h0000;
        zc[0][27] = 16'h0000;
        zc[0][28] = 16'h0000;
        zc[0][29] = 16'h0000;
        zc[0][30] = 16'h0000;
        zc[0][31] = 16'h0000;

        zc[1][0] =  16'h0800;   // set 1
        zc[1][1] =  16'h0800;
        zc[1][2] =  16'h0800;
        zc[1][3] =  16'h0800;
        zc[1][4] =  16'h0800;
        zc[1][5] =  16'h0800;
        zc[1][6] =  16'h0800;
        zc[1][7] =  16'h0800;
        zc[1][8] =  16'h0800;
        zc[1][9] =  16'h0800;
        zc[1][10] = 16'h0800;
        zc[1][11] = 16'h0800;
        zc[1][12] = 16'h0800;
        zc[1][13] = 16'h0800;
        zc[1][14] = 16'h0800;
        zc[1][15] = 16'h0800;
        zc[1][16] = 16'h0800;
        zc[1][17] = 16'h0800;
        zc[1][18] = 16'h0800;
        zc[1][19] = 16'h0800;
        zc[1][20] = 16'h0800;
        zc[1][21] = 16'h0800;
        zc[1][22] = 16'h0800;
        zc[1][23] = 16'h0800;
        zc[1][24] = 16'h0800;
        zc[1][25] = 16'h0800;
        zc[1][26] = 16'h0800;
        zc[1][27] = 16'h0800;
        zc[1][28] = 16'h0800;
        zc[1][29] = 16'h0800;
        zc[1][30] = 16'h0800;
        zc[1][31] = 16'h0800;
    
		zc[2][0] =  16'hFFFE;   // set 2
        zc[2][1] =  16'hFFF6;
        zc[2][2] =  16'hFFDC;
        zc[2][3] =  16'hFF9E;
        zc[2][4] =  16'hFF2A;
        zc[2][5] =  16'hFE82;
        zc[2][6] =  16'hFDCD;
        zc[2][7] =  16'hFD70;
        zc[2][8] =  16'hFE07;
        zc[2][9] =  16'h0044;
        zc[2][10] = 16'h04AE;
        zc[2][11] = 16'h0B4E;
        zc[2][12] = 16'h1380;
        zc[2][13] = 16'h1BF4;
        zc[2][14] = 16'h22F7;
        zc[2][15] = 16'h26F2;
        zc[2][16] = 16'h26F2;
        zc[2][17] = 16'h22F7;
        zc[2][18] = 16'h1BF4;
        zc[2][19] = 16'h1380;
        zc[2][20] = 16'h0B4E;
        zc[2][21] = 16'h04AE;
        zc[2][22] = 16'h0044;
        zc[2][23] = 16'hFE07;
        zc[2][24] = 16'hFD70;
        zc[2][25] = 16'hFDCD;
        zc[2][26] = 16'hFE82;
        zc[2][27] = 16'hFF2A;
        zc[2][28] = 16'hFF9E;
        zc[2][29] = 16'hFFDC;
        zc[2][30] = 16'hFFF6;
        zc[2][31] = 16'hFFFE;
    
        zc[3][0] =  16'h0000;   // set 3
        zc[3][1] =  16'h0000;
        zc[3][2] =  16'h0000;
        zc[3][3] =  16'h0000;
        zc[3][4] =  16'h0000;
        zc[3][5] =  16'h0000;
        zc[3][6] =  16'h0000;
        zc[3][7] =  16'h0000;
        zc[3][8] =  16'h0000;
        zc[3][9] =  16'h0000;
        zc[3][10] = 16'h0000;
        zc[3][11] = 16'h0000;
        zc[3][12] = 16'h0000;
        zc[3][13] = 16'h0000;
        zc[3][14] = 16'h0000;
        zc[3][15] = 16'h0000;
        zc[3][16] = 16'h0000;
        zc[3][17] = 16'h0000;
        zc[3][18] = 16'h0000;
        zc[3][19] = 16'h0000;
        zc[3][20] = 16'h0000;
        zc[3][21] = 16'h0000;
        zc[3][22] = 16'h0000;
        zc[3][23] = 16'h0000;
        zc[3][24] = 16'h0000;
        zc[3][25] = 16'h0000;
        zc[3][26] = 16'h0000;
        zc[3][27] = 16'h0000;
        zc[3][28] = 16'h0000;
        zc[3][29] = 16'h0000;
        zc[3][30] = 16'h0000;
        zc[3][31] = 16'h0000;
    end


    initial begin
        state = IDLE;
        timer_acc = 0;
        available = 1;
        ir_reg = 1;
        data_interrupt = 0;
    end

    always_ff @(posedge sys_clk) begin
        if(timer_acc == CLOCK_DIV) begin
            timer_acc <= 0;
        end
        else begin
            timer_acc <= new_timer_acc;
        end
        if(accel_ready==1) begin
            if(state==IDLE) begin
                if(timer_acc == CLOCK_DIV) begin
                    accel_enable <= 1;
                    available <= 0;
                    state <= READ_SETUP;
                end
            end
            else if(state==READ_SETUP) begin
                if(accel_busy==1) begin
                    state <= READ;
                end
            end
            else if(state==READ) begin
                accel_enable <= 0;
                if(accel_busy==0) begin
                    state <= FILTER_SETUP;
                end
            end
            else if(state==FILTER_SETUP) begin
                state <= FILTER;
                fir_enable <= 1;
            end
            else if(state==FILTER) begin
                fir_enable <= 0;
                if(fir_x_busy==0 && fir_y_busy==0 && fir_z_busy==0) begin
                    state <= HOLD;
                end
            end
            else if(state==HOLD) begin
                state <= IDLE;
                available <= 1;
            end
        end
        if(update_en==1) begin  // insert code to update coefficeint bank
            if(update_axis==1) begin    // update x-axis
                xc[update_bank][update_index] <= update_value;
            end
            else if(update_axis==2) begin   // update y-axis
                yc[update_bank][update_index] <= update_value;
            end
            else if(update_axis==3) begin   // update z-axis
                zc[update_bank][update_index] <= update_value;
            end
        end
        ir_reg <= available;
        if(ir_reg==0 && available==1) begin
            data_interrupt <= 1;
        end
        else begin
            data_interrupt <= 0;
        end
    end


    FIR_32_tap filter_x(
        .clk(sys_clk),
        .run(fir_enable),
        .busy(fir_x_busy),
        .sample_in(x),
        .filter_data(x_data),
        .coeff0(xc[x_bank][0]),
        .coeff1(xc[x_bank][1]),
        .coeff2(xc[x_bank][2]),
        .coeff3(xc[x_bank][3]),
        .coeff4(xc[x_bank][4]),
        .coeff5(xc[x_bank][5]),
        .coeff6(xc[x_bank][6]),
        .coeff7(xc[x_bank][7]),
        .coeff8(xc[x_bank][8]),
        .coeff9(xc[x_bank][9]),
        .coeff10(xc[x_bank][10]),
        .coeff11(xc[x_bank][11]),
        .coeff12(xc[x_bank][12]),
        .coeff13(xc[x_bank][13]),
        .coeff14(xc[x_bank][14]),
        .coeff15(xc[x_bank][15]),
        .coeff16(xc[x_bank][16]),
        .coeff17(xc[x_bank][17]),
        .coeff18(xc[x_bank][18]),
        .coeff19(xc[x_bank][19]),
        .coeff20(xc[x_bank][20]),
        .coeff21(xc[x_bank][21]),
        .coeff22(xc[x_bank][22]),
        .coeff23(xc[x_bank][23]),
        .coeff24(xc[x_bank][24]),
        .coeff25(xc[x_bank][25]),
        .coeff26(xc[x_bank][26]),
        .coeff27(xc[x_bank][27]),
        .coeff28(xc[x_bank][28]),
        .coeff29(xc[x_bank][29]),
        .coeff30(xc[x_bank][30]),
        .coeff31(xc[x_bank][31])
    );

    FIR_32_tap filter_y(
        .clk(sys_clk),
        .run(fir_enable),
        .busy(fir_y_busy),
        .sample_in(y),
        .filter_data(y_data),
        .coeff0(yc[y_bank][0]),
        .coeff1(yc[y_bank][1]),
        .coeff2(yc[y_bank][2]),
        .coeff3(yc[y_bank][3]),
        .coeff4(yc[y_bank][4]),
        .coeff5(yc[y_bank][5]),
        .coeff6(yc[y_bank][6]),
        .coeff7(yc[y_bank][7]),
        .coeff8(yc[y_bank][8]),
        .coeff9(yc[y_bank][9]),
        .coeff10(yc[y_bank][10]),
        .coeff11(yc[y_bank][11]),
        .coeff12(yc[y_bank][12]),
        .coeff13(yc[y_bank][13]),
        .coeff14(yc[y_bank][14]),
        .coeff15(yc[y_bank][15]),
        .coeff16(yc[y_bank][16]),
        .coeff17(yc[y_bank][17]),
        .coeff18(yc[y_bank][18]),
        .coeff19(yc[y_bank][19]),
        .coeff20(yc[y_bank][20]),
        .coeff21(yc[y_bank][21]),
        .coeff22(yc[y_bank][22]),
        .coeff23(yc[y_bank][23]),
        .coeff24(yc[y_bank][24]),
        .coeff25(yc[y_bank][25]),
        .coeff26(yc[y_bank][26]),
        .coeff27(yc[y_bank][27]),
        .coeff28(yc[y_bank][28]),
        .coeff29(yc[y_bank][29]),
        .coeff30(yc[y_bank][30]),
        .coeff31(yc[y_bank][31])
    );

    FIR_32_tap filter_z(
        .clk(sys_clk),
        .run(fir_enable),
        .busy(fir_z_busy),
        .sample_in(z),
        .filter_data(z_data),
        .coeff0(zc[z_bank][0]),
        .coeff1(zc[z_bank][1]),
        .coeff2(zc[z_bank][2]),
        .coeff3(zc[z_bank][3]),
        .coeff4(zc[z_bank][4]),
        .coeff5(zc[z_bank][5]),
        .coeff6(zc[z_bank][6]),
        .coeff7(zc[z_bank][7]),
        .coeff8(zc[z_bank][8]),
        .coeff9(zc[z_bank][9]),
        .coeff10(zc[z_bank][10]),
        .coeff11(zc[z_bank][11]),
        .coeff12(zc[z_bank][12]),
        .coeff13(zc[z_bank][13]),
        .coeff14(zc[z_bank][14]),
        .coeff15(zc[z_bank][15]),
        .coeff16(zc[z_bank][16]),
        .coeff17(zc[z_bank][17]),
        .coeff18(zc[z_bank][18]),
        .coeff19(zc[z_bank][19]),
        .coeff20(zc[z_bank][20]),
        .coeff21(zc[z_bank][21]),
        .coeff22(zc[z_bank][22]),
        .coeff23(zc[z_bank][23]),
        .coeff24(zc[z_bank][24]),
        .coeff25(zc[z_bank][25]),
        .coeff26(zc[z_bank][26]),
        .coeff27(zc[z_bank][27]),
        .coeff28(zc[z_bank][28]),
        .coeff29(zc[z_bank][29]),
        .coeff30(zc[z_bank][30]),
        .coeff31(zc[z_bank][31])
    );

    adxl345_controller accel(
        .clk(bus_clk),
        .clock_lock(pll_lock),
        .fetch(accel_enable),
        .busy(accel_busy),
        .ready(accel_ready),
        .x_axis(x),
        .y_axis(y),
        .z_axis(z),
        .spi_sclk(spi_sclk),
        .spi_mosi(spi_mosi),
        .spi_miso(spi_miso),
        .spi_cs(spi_cs)
    );


endmodule