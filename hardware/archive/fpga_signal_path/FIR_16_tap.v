module FIR_16_tap(
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
    input logic[15:0] coeff15
);
    typedef enum logic[2:0] {
        IDLE = 3'd0,
        FILTER = 3'd1,
        SUM = 3'd2
    } state_t;

    logic[2:0] state;
    logic status;
    logic fir_enable;

    logic[15:0] pipe_1_2;
    logic[15:0] pipe_2_3;
    logic[15:0] pipe_3_4;
    logic[15:0] sinkhole;

    logic[15:0] f1;
    logic[15:0] f2;
    logic[15:0] f3;
    logic[15:0] f4;
    logic[15:0] sum;

    wire[15:0] data_in;
    assign data_in = sample_in;

    initial begin
        state = IDLE;
        status = 0;
        fir_enable=0;
        filter_data = 0;
    end

    always_comb begin
        busy = run | status;
        sum = f1 + f2 + f3 + f4;
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
            state <= SUM;
            fir_enable <= 0;
        end
        else if(state==SUM) begin
            state <= IDLE;
            filter_data <= sum;
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
        .sample_out(sinkhole),
        .acc_out(f4)
    );

endmodule