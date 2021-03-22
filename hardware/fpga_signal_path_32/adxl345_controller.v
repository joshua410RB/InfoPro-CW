module adxl345_controller(
    input logic clk,
    input logic clock_lock,
    input logic fetch,
    output logic ready,
    output logic busy,

    output logic[15:0] x_axis,
    output logic[15:0] y_axis,
    output logic[15:0] z_axis,

    output logic spi_sclk,
    output logic spi_mosi,  // SDI
    input logic spi_miso,  // SDO
    output logic spi_cs
);
    typedef enum logic[3:0] {
        INIT = 4'd0,
        CONFIG_SETUP = 4'd1,
        CONFIG = 4'd2,
        IDLE = 4'd3,
        READ_SETUP = 4'd4,
        READ_X = 4'd5,
        READ_Y = 4'd6,
        READ_Z = 4'd7,
        SPACE = 4'd8
    } state_t;

    logic[3:0] state;
    logic[5:0] reg_address;
    logic[7:0] addr_header;
    logic rw;
    logic mb;
    logic bus_clk;
    logic status;

    logic[15:0] x_data;
    logic[15:0] y_data;
    logic[15:0] z_data;

    logic[2:0] counter1;
    logic[2:0] write_counter;
    logic[3:0] read_counter;

    logic[7:0] writedata;

    wire[2:0] new_counter1;
    wire[2:0] new_write_counter;
    wire[3:0] new_read_counter;

    assign new_counter1 = counter1 - 1;
    assign new_write_counter = write_counter - 1;
    assign new_read_counter = read_counter - 1;

    initial begin
        state=INIT;
        counter1=7;
        write_counter=7;
        read_counter=15;
        reg_address = 6'd49;
        rw=0;
        mb=0;
        ready=0;
        status=1;
        x_axis=0;
        x_data=0;
        y_axis=0;
        y_data=0;
        z_axis=0;
        z_data=0;
        writedata=0;
    end

    always_comb begin
        addr_header[5:0] = reg_address;
        addr_header[6] = mb;         // MB bit
        addr_header[7] = rw;

        bus_clk = !clk;
        spi_cs = (state==SPACE) ? 1 : !(status | fetch);
        busy = status;

        if(state==CONFIG) begin
            spi_mosi = writedata[write_counter];
        end
        else begin
            spi_mosi = addr_header[counter1];
        end

        if(state!=INIT && state!=IDLE && state!=SPACE) begin
            spi_sclk = bus_clk;
        end
        else begin
            spi_sclk = 1;
        end
    end

    always_ff @(posedge clk) begin
        if(state==INIT) begin
            if(clock_lock==1) begin
                reg_address <= 6'd49;
                rw <= 0;
                mb <= 0;
                ready <= 0;
                status <= 1;
                state <= CONFIG_SETUP;
            end
        end
        else if(state==CONFIG_SETUP) begin
            counter1 <= new_counter1;
            if(counter1==0) begin
                state <= CONFIG;
            end
        end
        else if(state==CONFIG) begin
            write_counter <= new_write_counter;
            if(write_counter==0) begin
                reg_address <= 6'd50;
                rw <= 1;
                mb <= 1;
                state <= SPACE;
            end
        end
        else if (state==IDLE) begin
           if(fetch==1) begin
               state <= READ_SETUP;
               status <= 1;
           end 
        end
        else if(state==READ_SETUP) begin
            counter1 <= new_counter1;
            if(counter1==0) begin
                state <= READ_X;
            end
        end
        else if(state==READ_X) begin
            read_counter <= new_read_counter;
            if(read_counter==0) begin
                state <= READ_Y;
            end
        end
        else if(state==READ_Y) begin
            read_counter <= new_read_counter;
            if(read_counter==0) begin
                state <= READ_Z;
            end
        end
        else if(state==READ_Z) begin
            read_counter <= new_read_counter;
            if(read_counter==0) begin
                state <= SPACE;
            end
        end
        else if(state==SPACE) begin
            state <= IDLE;
            ready <= 1;
            status <= 0;

            x_axis[15:8] <= x_data[7:0];
            x_axis[7:0] <= x_data[15:8];

            y_axis[15:8] <= y_data[7:0];
            y_axis[7:0] <= y_data[15:8];

            z_axis[15:8] <= z_data[7:0];
            z_axis[7:0] <= z_data[15:8];
        end
    end

    always_ff @(posedge bus_clk) begin
        if(state==READ_X) begin
            x_data[read_counter] <= spi_miso;
        end
        else if(state==READ_Y) begin
            y_data[read_counter] <= spi_miso;
        end
        else if(state==READ_Z) begin
            z_data[read_counter] <= spi_miso;
        end
    end

endmodule