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
    input logic[16:0] update_value,

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

    logic[16:0] xc[3:0][31:0];  // x coefficients (4 banks of 16 values each)
    logic[16:0] yc[3:0][31:0];  // y coefficients
    logic[16:0] zc[3:0][31:0];  // z coefficients

    initial begin   // initialise x coefficients
        xc[0][0] =  17'h00800;   // set 0
        xc[0][1] =  17'h00800;
        xc[0][2] =  17'h00800;
        xc[0][3] =  17'h00800;
        xc[0][4] =  17'h00800;
        xc[0][5] =  17'h00800;
        xc[0][6] =  17'h00800;
        xc[0][7] =  17'h00800;
        xc[0][8] =  17'h00800;
        xc[0][9] =  17'h00800;
        xc[0][10] = 17'h00800;
        xc[0][11] = 17'h00800;
        xc[0][12] = 17'h00800;
        xc[0][13] = 17'h00800;
        xc[0][14] = 17'h00800;
        xc[0][15] = 17'h00800;
        xc[0][16] = 17'h00800;
        xc[0][17] = 17'h00800;
        xc[0][18] = 17'h00800;
        xc[0][19] = 17'h00800;
        xc[0][20] = 17'h00800;
        xc[0][21] = 17'h00800;
        xc[0][22] = 17'h00800;
        xc[0][23] = 17'h00800;
        xc[0][24] = 17'h00800;
        xc[0][25] = 17'h00800;
        xc[0][26] = 17'h00800;
        xc[0][27] = 17'h00800;
        xc[0][28] = 17'h00800;
        xc[0][29] = 17'h00800;
        xc[0][30] = 17'h00800;
        xc[0][31] = 17'h00800;

        xc[1][0] =  17'h00400;   // set 1
        xc[1][1] =  17'h00400;
        xc[1][2] =  17'h00400;
        xc[1][3] =  17'h00400;
        xc[1][4] =  17'h00400;
        xc[1][5] =  17'h00400;
        xc[1][6] =  17'h00400;
        xc[1][7] =  17'h00400;
        xc[1][8] =  17'h00400;
        xc[1][9] =  17'h00400;
        xc[1][10] = 17'h00400;
        xc[1][11] = 17'h00400;
        xc[1][12] = 17'h00400;
        xc[1][13] = 17'h00400;
        xc[1][14] = 17'h00400;
        xc[1][15] = 17'h00400;
        xc[1][16] = 17'h00400;
        xc[1][17] = 17'h00400;
        xc[1][18] = 17'h00400;
        xc[1][19] = 17'h00400;
        xc[1][20] = 17'h00400;
        xc[1][21] = 17'h00400;
        xc[1][22] = 17'h00400;
        xc[1][23] = 17'h00400;
        xc[1][24] = 17'h00400;
        xc[1][25] = 17'h00400;
        xc[1][26] = 17'h00400;
        xc[1][27] = 17'h00400;
        xc[1][28] = 17'h00400;
        xc[1][29] = 17'h00400;
        xc[1][30] = 17'h00400;
        xc[1][31] = 17'h00400;

		xc[2][0] =  17'h1FFFE;   // set 2
        xc[2][1] =  17'h1FFF6;
        xc[2][2] =  17'h1FFDC;
        xc[2][3] =  17'h1FF9E;
        xc[2][4] =  17'h1FF2A;
        xc[2][5] =  17'h1FE82;
        xc[2][6] =  17'h1FDCD;
        xc[2][7] =  17'h1FD70;
        xc[2][8] =  17'h1FE07;
        xc[2][9] =  17'h00044;
        xc[2][10] = 17'h004AE;
        xc[2][11] = 17'h00B4E;
        xc[2][12] = 17'h01380;
        xc[2][13] = 17'h01BF4;
        xc[2][14] = 17'h022F7;
        xc[2][15] = 17'h026F2;
        xc[2][16] = 17'h026F2;
        xc[2][17] = 17'h022F7;
        xc[2][18] = 17'h01BF4;
        xc[2][19] = 17'h01380;
        xc[2][20] = 17'h00B4E;
        xc[2][21] = 17'h004AE;
        xc[2][22] = 17'h00044;
        xc[2][23] = 17'h1FE07;
        xc[2][24] = 17'h1FD70;
        xc[2][25] = 17'h1FDCD;
        xc[2][26] = 17'h1FE82;
        xc[2][27] = 17'h1FF2A;
        xc[2][28] = 17'h1FF9E;
        xc[2][29] = 17'h1FFDC;
        xc[2][30] = 17'h1FFF6;
        xc[2][31] = 17'h1FFFE;

        xc[3][0] =  17'h00000;   // set 3
        xc[3][1] =  17'h00000;
        xc[3][2] =  17'h00000;
        xc[3][3] =  17'h00000;
        xc[3][4] =  17'h00000;
        xc[3][5] =  17'h00000;
        xc[3][6] =  17'h00000;
        xc[3][7] =  17'h00000;
        xc[3][8] =  17'h00000;
        xc[3][9] =  17'h00000;
        xc[3][10] = 17'h00000;
        xc[3][11] = 17'h00000;
        xc[3][12] = 17'h00000;
        xc[3][13] = 17'h00000;
        xc[3][14] = 17'h00000;
        xc[3][15] = 17'h00000;
        xc[3][16] = 17'h00000;
        xc[3][17] = 17'h00000;
        xc[3][18] = 17'h00000;
        xc[3][19] = 17'h00000;
        xc[3][20] = 17'h00000;
        xc[3][21] = 17'h00000;
        xc[3][22] = 17'h00000;
        xc[3][23] = 17'h00000;
        xc[3][24] = 17'h00000;
        xc[3][25] = 17'h00000;
        xc[3][26] = 17'h00000;
        xc[3][27] = 17'h00000;
        xc[3][28] = 17'h00000;
        xc[3][29] = 17'h00000;
        xc[3][30] = 17'h00000;
        xc[3][31] = 17'h00000;
    end

    initial begin   // initialise y coefficients
        yc[0][0] =  17'h00800;   // set 0
        yc[0][1] =  17'h00800;
        yc[0][2] =  17'h00800;
        yc[0][3] =  17'h00800;
        yc[0][4] =  17'h00800;
        yc[0][5] =  17'h00800;
        yc[0][6] =  17'h00800;
        yc[0][7] =  17'h00800;
        yc[0][8] =  17'h00800;
        yc[0][9] =  17'h00800;
        yc[0][10] = 17'h00800;
        yc[0][11] = 17'h00800;
        yc[0][12] = 17'h00800;
        yc[0][13] = 17'h00800;
        yc[0][14] = 17'h00800;
        yc[0][15] = 17'h00800;
        yc[0][16] = 17'h00800;
        yc[0][17] = 17'h00800;
        yc[0][18] = 17'h00800;
        yc[0][19] = 17'h00800;
        yc[0][20] = 17'h00800;
        yc[0][21] = 17'h00800;
        yc[0][22] = 17'h00800;
        yc[0][23] = 17'h00800;
        yc[0][24] = 17'h00800;
        yc[0][25] = 17'h00800;
        yc[0][26] = 17'h00800;
        yc[0][27] = 17'h00800;
        yc[0][28] = 17'h00800;
        yc[0][29] = 17'h00800;
        yc[0][30] = 17'h00800;
        yc[0][31] = 17'h00800;

        yc[1][0] =  17'h00400;   // set 1
        yc[1][1] =  17'h00400;
        yc[1][2] =  17'h00400;
        yc[1][3] =  17'h00400;
        yc[1][4] =  17'h00400;
        yc[1][5] =  17'h00400;
        yc[1][6] =  17'h00400;
        yc[1][7] =  17'h00400;
        yc[1][8] =  17'h00400;
        yc[1][9] =  17'h00400;
        yc[1][10] = 17'h00400;
        yc[1][11] = 17'h00400;
        yc[1][12] = 17'h00400;
        yc[1][13] = 17'h00400;
        yc[1][14] = 17'h00400;
        yc[1][15] = 17'h00400;
        yc[1][16] = 17'h00400;
        yc[1][17] = 17'h00400;
        yc[1][18] = 17'h00400;
        yc[1][19] = 17'h00400;
        yc[1][20] = 17'h00400;
        yc[1][21] = 17'h00400;
        yc[1][22] = 17'h00400;
        yc[1][23] = 17'h00400;
        yc[1][24] = 17'h00400;
        yc[1][25] = 17'h00400;
        yc[1][26] = 17'h00400;
        yc[1][27] = 17'h00400;
        yc[1][28] = 17'h00400;
        yc[1][29] = 17'h00400;
        yc[1][30] = 17'h00400;
        yc[1][31] = 17'h00400;

		yc[2][0] =  17'h1FFFE;   // set 2
        yc[2][1] =  17'h1FFF6;
        yc[2][2] =  17'h1FFDC;
        yc[2][3] =  17'h1FF9E;
        yc[2][4] =  17'h1FF2A;
        yc[2][5] =  17'h1FE82;
        yc[2][6] =  17'h1FDCD;
        yc[2][7] =  17'h1FD70;
        yc[2][8] =  17'h1FE07;
        yc[2][9] =  17'h00044;
        yc[2][10] = 17'h004AE;
        yc[2][11] = 17'h00B4E;
        yc[2][12] = 17'h01380;
        yc[2][13] = 17'h01BF4;
        yc[2][14] = 17'h022F7;
        yc[2][15] = 17'h026F2;
        yc[2][16] = 17'h026F2;
        yc[2][17] = 17'h022F7;
        yc[2][18] = 17'h01BF4;
        yc[2][19] = 17'h01380;
        yc[2][20] = 17'h00B4E;
        yc[2][21] = 17'h004AE;
        yc[2][22] = 17'h00044;
        yc[2][23] = 17'h1FE07;
        yc[2][24] = 17'h1FD70;
        yc[2][25] = 17'h1FDCD;
        yc[2][26] = 17'h1FE82;
        yc[2][27] = 17'h1FF2A;
        yc[2][28] = 17'h1FF9E;
        yc[2][29] = 17'h1FFDC;
        yc[2][30] = 17'h1FFF6;
        yc[2][31] = 17'h1FFFE;

        yc[3][0] =  17'h00000;   // set 3
        yc[3][1] =  17'h00000;
        yc[3][2] =  17'h00000;
        yc[3][3] =  17'h00000;
        yc[3][4] =  17'h00000;
        yc[3][5] =  17'h00000;
        yc[3][6] =  17'h00000;
        yc[3][7] =  17'h00000;
        yc[3][8] =  17'h00000;
        yc[3][9] =  17'h00000;
        yc[3][10] = 17'h00000;
        yc[3][11] = 17'h00000;
        yc[3][12] = 17'h00000;
        yc[3][13] = 17'h00000;
        yc[3][14] = 17'h00000;
        yc[3][15] = 17'h00000;
        yc[3][16] = 17'h00000;
        yc[3][17] = 17'h00000;
        yc[3][18] = 17'h00000;
        yc[3][19] = 17'h00000;
        yc[3][20] = 17'h00000;
        yc[3][21] = 17'h00000;
        yc[3][22] = 17'h00000;
        yc[3][23] = 17'h00000;
        yc[3][24] = 17'h00000;
        yc[3][25] = 17'h00000;
        yc[3][26] = 17'h00000;
        yc[3][27] = 17'h00000;
        yc[3][28] = 17'h00000;
        yc[3][29] = 17'h00000;
        yc[3][30] = 17'h00000;
        yc[3][31] = 17'h00000;
    end

    initial begin   // initialise z coefficients
        zc[0][0] =  17'h00800;   // set 0
        zc[0][1] =  17'h00800;
        zc[0][2] =  17'h00800;
        zc[0][3] =  17'h00800;
        zc[0][4] =  17'h00800;
        zc[0][5] =  17'h00800;
        zc[0][6] =  17'h00800;
        zc[0][7] =  17'h00800;
        zc[0][8] =  17'h00800;
        zc[0][9] =  17'h00800;
        zc[0][10] = 17'h00800;
        zc[0][11] = 17'h00800;
        zc[0][12] = 17'h00800;
        zc[0][13] = 17'h00800;
        zc[0][14] = 17'h00800;
        zc[0][15] = 17'h00800;
        zc[0][16] = 17'h00800;
        zc[0][17] = 17'h00800;
        zc[0][18] = 17'h00800;
        zc[0][19] = 17'h00800;
        zc[0][20] = 17'h00800;
        zc[0][21] = 17'h00800;
        zc[0][22] = 17'h00800;
        zc[0][23] = 17'h00800;
        zc[0][24] = 17'h00800;
        zc[0][25] = 17'h00800;
        zc[0][26] = 17'h00800;
        zc[0][27] = 17'h00800;
        zc[0][28] = 17'h00800;
        zc[0][29] = 17'h00800;
        zc[0][30] = 17'h00800;
        zc[0][31] = 17'h00800;
    
        zc[1][0] =  17'h00400;   // set 1
        zc[1][1] =  17'h00400;
        zc[1][2] =  17'h00400;
        zc[1][3] =  17'h00400;
        zc[1][4] =  17'h00400;
        zc[1][5] =  17'h00400;
        zc[1][6] =  17'h00400;
        zc[1][7] =  17'h00400;
        zc[1][8] =  17'h00400;
        zc[1][9] =  17'h00400;
        zc[1][10] = 17'h00400;
        zc[1][11] = 17'h00400;
        zc[1][12] = 17'h00400;
        zc[1][13] = 17'h00400;
        zc[1][14] = 17'h00400;
        zc[1][15] = 17'h00400;
        zc[1][16] = 17'h00400;
        zc[1][17] = 17'h00400;
        zc[1][18] = 17'h00400;
        zc[1][19] = 17'h00400;
        zc[1][20] = 17'h00400;
        zc[1][21] = 17'h00400;
        zc[1][22] = 17'h00400;
        zc[1][23] = 17'h00400;
        zc[1][24] = 17'h00400;
        zc[1][25] = 17'h00400;
        zc[1][26] = 17'h00400;
        zc[1][27] = 17'h00400;
        zc[1][28] = 17'h00400;
        zc[1][29] = 17'h00400;
        zc[1][30] = 17'h00400;
        zc[1][31] = 17'h00400;
    
		zc[2][0] =  17'h1FFFE;   // set 2
        zc[2][1] =  17'h1FFF6;
        zc[2][2] =  17'h1FFDC;
        zc[2][3] =  17'h1FF9E;
        zc[2][4] =  17'h1FF2A;
        zc[2][5] =  17'h1FE82;
        zc[2][6] =  17'h1FDCD;
        zc[2][7] =  17'h1FD70;
        zc[2][8] =  17'h1FE07;
        zc[2][9] =  17'h00044;
        zc[2][10] = 17'h004AE;
        zc[2][11] = 17'h00B4E;
        zc[2][12] = 17'h01380;
        zc[2][13] = 17'h01BF4;
        zc[2][14] = 17'h022F7;
        zc[2][15] = 17'h026F2;
        zc[2][16] = 17'h026F2;
        zc[2][17] = 17'h022F7;
        zc[2][18] = 17'h01BF4;
        zc[2][19] = 17'h01380;
        zc[2][20] = 17'h00B4E;
        zc[2][21] = 17'h004AE;
        zc[2][22] = 17'h00044;
        zc[2][23] = 17'h1FE07;
        zc[2][24] = 17'h1FD70;
        zc[2][25] = 17'h1FDCD;
        zc[2][26] = 17'h1FE82;
        zc[2][27] = 17'h1FF2A;
        zc[2][28] = 17'h1FF9E;
        zc[2][29] = 17'h1FFDC;
        zc[2][30] = 17'h1FFF6;
        zc[2][31] = 17'h1FFFE;
    
        zc[3][0] =  17'h00000;   // set 3
        zc[3][1] =  17'h00000;
        zc[3][2] =  17'h00000;
        zc[3][3] =  17'h00000;
        zc[3][4] =  17'h00000;
        zc[3][5] =  17'h00000;
        zc[3][6] =  17'h00000;
        zc[3][7] =  17'h00000;
        zc[3][8] =  17'h00000;
        zc[3][9] =  17'h00000;
        zc[3][10] = 17'h00000;
        zc[3][11] = 17'h00000;
        zc[3][12] = 17'h00000;
        zc[3][13] = 17'h00000;
        zc[3][14] = 17'h00000;
        zc[3][15] = 17'h00000;
        zc[3][16] = 17'h00000;
        zc[3][17] = 17'h00000;
        zc[3][18] = 17'h00000;
        zc[3][19] = 17'h00000;
        zc[3][20] = 17'h00000;
        zc[3][21] = 17'h00000;
        zc[3][22] = 17'h00000;
        zc[3][23] = 17'h00000;
        zc[3][24] = 17'h00000;
        zc[3][25] = 17'h00000;
        zc[3][26] = 17'h00000;
        zc[3][27] = 17'h00000;
        zc[3][28] = 17'h00000;
        zc[3][29] = 17'h00000;
        zc[3][30] = 17'h00000;
        zc[3][31] = 17'h00000;
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