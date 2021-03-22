module signal_path_16_tap(
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
    input logic[3:0] update_index,
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

    logic[15:0] xc[3:0][15:0];  // x coefficients (4 banks of 16 values each)
    logic[15:0] yc[3:0][15:0];  // y coefficients
    logic[15:0] zc[3:0][15:0];  // z coefficients

    initial begin   // initialise x coefficients
        xc[0][0] = 16'hffff;   // set 0
        xc[0][1] = 0;
        xc[0][2] = 0;
        xc[0][3] = 0;
        xc[0][4] = 0;
        xc[0][5] = 0;
        xc[0][6] = 0;
        xc[0][7] = 0;
        xc[0][8] = 0;
        xc[0][9] = 0;
        xc[0][10] = 0;
        xc[0][11] = 0;
        xc[0][12] = 0;
        xc[0][13] = 0;
        xc[0][14] = 0;
        xc[0][15] = 0;

        xc[1][0] = 16'h1000;   // set 1
        xc[1][1] = 16'h1000;
        xc[1][2] = 16'h1000;
        xc[1][3] = 16'h1000;
        xc[1][4] = 16'h1000;
        xc[1][5] = 16'h1000;
        xc[1][6] = 16'h1000;
        xc[1][7] = 16'h1000;
        xc[1][8] = 16'h1000;
        xc[1][9] = 16'h1000;
        xc[1][10] = 16'h1000;
        xc[1][11] = 16'h1000;
        xc[1][12] = 16'h1000;
        xc[1][13] = 16'h1000;
        xc[1][14] = 16'h1000;
        xc[1][15] = 16'h1000;

        xc[2][0] = 0;   // set 2
        xc[2][1] = 0;
        xc[2][2] = 16'h4000;
        xc[2][3] = 16'h4000;
        xc[2][4] = 16'h4000;
        xc[2][5] = 16'h4000;
        xc[2][6] = 0;
        xc[2][7] = 0;
        xc[2][8] = 0;
        xc[2][9] = 0;
        xc[2][10] = 0;
        xc[2][11] = 0;
        xc[2][12] = 0;
        xc[2][13] = 0;
        xc[2][14] = 0;
        xc[2][15] = 0;

        xc[3][0] = 0;   // set 3
        xc[3][1] = 0;
        xc[3][2] = 0;
        xc[3][3] = 0;
        xc[3][4] = 0;
        xc[3][5] = 0;
        xc[3][6] = 0;
        xc[3][7] = 0;
        xc[3][8] = 0;
        xc[3][9] = 0;
        xc[3][10] = 0;
        xc[3][11] = 0;
        xc[3][12] = 0;
        xc[3][13] = 0;
        xc[3][14] = 0;
        xc[3][15] = 0;
    end

    initial begin   // initialise y coefficients
        yc[0][0] = 16'hffff;   // set 0
        yc[0][1] = 0;
        yc[0][2] = 0;
        yc[0][3] = 0;
        yc[0][4] = 0;
        yc[0][5] = 0;
        yc[0][6] = 0;
        yc[0][7] = 0;
        yc[0][8] = 0;
        yc[0][9] = 0;
        yc[0][10] = 0;
        yc[0][11] = 0;
        yc[0][12] = 0;
        yc[0][13] = 0;
        yc[0][14] = 0;
        yc[0][15] = 0;

        yc[1][0] = 16'h1000;   // set 1
        yc[1][1] = 16'h1000;
        yc[1][2] = 16'h1000;
        yc[1][3] = 16'h1000;
        yc[1][4] = 16'h1000;
        yc[1][5] = 16'h1000;
        yc[1][6] = 16'h1000;
        yc[1][7] = 16'h1000;
        yc[1][8] = 16'h1000;
        yc[1][9] = 16'h1000;
        yc[1][10] = 16'h1000;
        yc[1][11] = 16'h1000;
        yc[1][12] = 16'h1000;
        yc[1][13] = 16'h1000;
        yc[1][14] = 16'h1000;
        yc[1][15] = 16'h1000;

        yc[2][0] = 0;   // set 2
        yc[2][1] = 0;
        yc[2][2] = 16'h4000;
        yc[2][3] = 16'h4000;
        yc[2][4] = 16'h4000;
        yc[2][5] = 16'h4000;
        yc[2][6] = 0;
        yc[2][7] = 0;
        yc[2][8] = 0;
        yc[2][9] = 0;
        yc[2][10] = 0;
        yc[2][11] = 0;
        yc[2][12] = 0;
        yc[2][13] = 0;
        yc[2][14] = 0;
        yc[2][15] = 0;

        yc[3][0] = 0;   // set 3
        yc[3][1] = 0;
        yc[3][2] = 0;
        yc[3][3] = 0;
        yc[3][4] = 0;
        yc[3][5] = 0;
        yc[3][6] = 0;
        yc[3][7] = 0;
        yc[3][8] = 0;
        yc[3][9] = 0;
        yc[3][10] = 0;
        yc[3][11] = 0;
        yc[3][12] = 0;
        yc[3][13] = 0;
        yc[3][14] = 0;
        yc[3][15] = 0;
    end

    initial begin   // initialise z coefficients
        zc[0][0] = 16'hffff;   // set 0
        zc[0][1] = 0;
        zc[0][2] = 0;
        zc[0][3] = 0;
        zc[0][4] = 0;
        zc[0][5] = 0;
        zc[0][6] = 0;
        zc[0][7] = 0;
        zc[0][8] = 0;
        zc[0][9] = 0;
        zc[0][10] = 0;
        zc[0][11] = 0;
        zc[0][12] = 0;
        zc[0][13] = 0;
        zc[0][14] = 0;
        zc[0][15] = 0;

        zc[1][0] = 16'h1000;   // set 1
        zc[1][1] = 16'h1000;
        zc[1][2] = 16'h1000;
        zc[1][3] = 16'h1000;
        zc[1][4] = 16'h1000;
        zc[1][5] = 16'h1000;
        zc[1][6] = 16'h1000;
        zc[1][7] = 16'h1000;
        zc[1][8] = 16'h1000;
        zc[1][9] = 16'h1000;
        zc[1][10] = 16'h1000;
        zc[1][11] = 16'h1000;
        zc[1][12] = 16'h1000;
        zc[1][13] = 16'h1000;
        zc[1][14] = 16'h1000;
        zc[1][15] = 16'h1000;

        zc[2][0] = 0;   // set 2
        zc[2][1] = 0;
        zc[2][2] = 16'h4000;
        zc[2][3] = 16'h4000;
        zc[2][4] = 16'h4000;
        zc[2][5] = 16'h4000;
        zc[2][6] = 0;
        zc[2][7] = 0;
        zc[2][8] = 0;
        zc[2][9] = 0;
        zc[2][10] = 0;
        zc[2][11] = 0;
        zc[2][12] = 0;
        zc[2][13] = 0;
        zc[2][14] = 0;
        zc[2][15] = 0;

        zc[3][0] = 0;   // set 3
        zc[3][1] = 0;
        zc[3][2] = 0;
        zc[3][3] = 0;
        zc[3][4] = 0;
        zc[3][5] = 0;
        zc[3][6] = 0;
        zc[3][7] = 0;
        zc[3][8] = 0;
        zc[3][9] = 0;
        zc[3][10] = 0;
        zc[3][11] = 0;
        zc[3][12] = 0;
        zc[3][13] = 0;
        zc[3][14] = 0;
        zc[3][15] = 0;
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


    FIR_16_tap filter_x(
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
        .coeff15(xc[x_bank][15])
    );

    FIR_16_tap filter_y(
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
        .coeff15(yc[y_bank][15])
    );

    FIR_16_tap filter_z(
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
        .coeff15(zc[z_bank][15])
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