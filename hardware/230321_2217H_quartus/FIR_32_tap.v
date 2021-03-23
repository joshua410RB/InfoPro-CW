module FIR_32_tap(
    input logic clk,
    input logic run,
    output logic busy,

    input logic[15:0] sample_in,
    output logic[15:0] filter_data,

    input logic[15:0] coeff0,
    input logic[15:0] coeff1,
    input logic[15:0] coeff2,
    input logic[15:0] coeff3,
    
    input logic[15:0] coeff4,
    input logic[15:0] coeff5,
    input logic[15:0] coeff6,
    input logic[15:0] coeff7,

    input logic[15:0] coeff8,
    input logic[15:0] coeff9,
    input logic[15:0] coeff10,
    input logic[15:0] coeff11,

    input logic[15:0] coeff12,
    input logic[15:0] coeff13,
    input logic[15:0] coeff14,
    input logic[15:0] coeff15,

    input logic[15:0] coeff16,
    input logic[15:0] coeff17,
    input logic[15:0] coeff18,
    input logic[15:0] coeff19,

    input logic[15:0] coeff20,
    input logic[15:0] coeff21,
    input logic[15:0] coeff22,
    input logic[15:0] coeff23,

    input logic[15:0] coeff24,
    input logic[15:0] coeff25,
    input logic[15:0] coeff26,
    input logic[15:0] coeff27,
    
    input logic[15:0] coeff28,
    input logic[15:0] coeff29,
    input logic[15:0] coeff30,
    input logic[15:0] coeff31
);
    typedef enum logic[2:0] {
        IDLE = 3'd0,
        FILTER = 3'd1,
        SUM1 = 3'd2,
        SUM2 = 3'd3
    } state_t;

    logic[2:0] state;
    logic status;
    logic fir_enable;

    logic[15:0] pipe_1_2;
    logic[15:0] pipe_2_3;
    logic[15:0] pipe_3_4;
    logic[15:0] pipe_4_5;
    logic[15:0] pipe_5_6;
    logic[15:0] pipe_6_7;
    logic[15:0] pipe_7_8;
    logic[15:0] sinkhole;

    logic[31:0] f1;
    logic[31:0] f2;
    logic[31:0] f3;
    logic[31:0] f4;
    logic[31:0] f5;
    logic[31:0] f6;
    logic[31:0] f7;
    logic[31:0] f8;
    logic[31:0] sum1;
    logic[31:0] sum2;
    logic[31:0] final_sum;

    wire[15:0] data_in;
    assign data_in = sample_in;

    initial begin
        state = IDLE;
        status = 0;
        fir_enable=0;
        filter_data = 0;
        sum1=0;
        sum2=0;
    end

    always_comb begin
        busy = run | status;
        // sum1 = f1 + f2 + f3 + f4;
        // sum2 = f5 + f6 + f7 + f8;
        final_sum = sum1 + sum2;
    end

    always_ff @(posedge clk) begin
        if(state==IDLE) begin
            if(run==1) begin
                state <= FILTER;
                status <= 1;
                fir_enable <= 1;
            end
        end
        else if(state==FILTER) begin
            state <= SUM1;
            fir_enable <= 0;
        end
        else if(state==SUM1) begin
            state <= SUM2;
            sum1 <= f1+f2+f3+f4;
            sum2 <= f5+f6+f7+f8;
        end
        else if(state==SUM2) begin
            state <= IDLE;
            filter_data <= final_sum[31:16];
            status <= 0;
        end
    end

    FIR_4_tap tap_bank_1(
        .clk(clk),
        .enable(fir_enable),
        .sample_in(sample_in),
        .coeff1(coeff0),
        .coeff2(coeff1),
        .coeff3(coeff2),
        .coeff4(coeff3),
        .acc_in({16'd0}),
        .sample_out(pipe_1_2),
        .acc_out(f1)
    );

    FIR_4_tap tap_bank_2(
        .clk(clk),
        .enable(fir_enable),
        .sample_in(pipe_1_2),
        .coeff1(coeff4),
        .coeff2(coeff5),
        .coeff3(coeff6),
        .coeff4(coeff7),
        .acc_in({16'd0}),
        .sample_out(pipe_2_3),
        .acc_out(f2)
    );

    FIR_4_tap tap_bank_3(
        .clk(clk),
        .enable(fir_enable),
        .sample_in(pipe_2_3),
        .coeff1(coeff8),
        .coeff2(coeff9),
        .coeff3(coeff10),
        .coeff4(coeff11),
        .acc_in({16'd0}),
        .sample_out(pipe_3_4),
        .acc_out(f3)
    );

    FIR_4_tap tap_bank_4(
        .clk(clk),
        .enable(fir_enable),
        .sample_in(pipe_3_4),
        .coeff1(coeff12),
        .coeff2(coeff13),
        .coeff3(coeff14),
        .coeff4(coeff15),
        .acc_in({16'd0}),
        .sample_out(pipe_4_5),
        .acc_out(f4)
    );

    FIR_4_tap tap_bank_5(
        .clk(clk),
        .enable(fir_enable),
        .sample_in(pipe_4_5),
        .coeff1(coeff16),
        .coeff2(coeff17),
        .coeff3(coeff18),
        .coeff4(coeff19),
        .acc_in({16'd0}),
        .sample_out(pipe_5_6),
        .acc_out(f5)
    );

    FIR_4_tap tap_bank_6(
        .clk(clk),
        .enable(fir_enable),
        .sample_in(pipe_5_6),
        .coeff1(coeff20),
        .coeff2(coeff21),
        .coeff3(coeff22),
        .coeff4(coeff23),
        .acc_in({16'd0}),
        .sample_out(pipe_6_7),
        .acc_out(f6)
    );

    FIR_4_tap tap_bank_7(
        .clk(clk),
        .enable(fir_enable),
        .sample_in(pipe_6_7),
        .coeff1(coeff24),
        .coeff2(coeff25),
        .coeff3(coeff26),
        .coeff4(coeff27),
        .acc_in({16'd0}),
        .sample_out(pipe_7_8),
        .acc_out(f7)
    );

    FIR_4_tap tap_bank_8(
        .clk(clk),
        .enable(fir_enable),
        .sample_in(pipe_7_8),
        .coeff1(coeff28),
        .coeff2(coeff29),
        .coeff3(coeff30),
        .coeff4(coeff31),
        .acc_in({16'd0}),
        .sample_out(sinkhole),
        .acc_out(f8)
    );

endmodule