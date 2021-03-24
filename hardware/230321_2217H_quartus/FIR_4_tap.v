module FIR_4_tap(
    input logic clk,
    input logic enable,
    input logic[15:0] sample_in,
    input logic[15:0] coeff1,
    input logic[15:0] coeff2,
    input logic[15:0] coeff3,
    input logic[15:0] coeff4,
    input logic[15:0] acc_in,
    output logic[15:0] sample_out,
    output logic[31:0] acc_out
);
    logic[15:0] temp1;
    logic[15:0] temp2;
    logic[15:0] temp3;

    logic[31:0] mult1;
    logic[31:0] mult2;
    logic[31:0] mult3;
    logic[31:0] mult4;
    logic[31:0] sum;

    initial begin
        sample_out = 0;
        acc_out = 0;
        temp1 = 0;
        temp2 = 0;
        temp3 = 0;
    end

    always_comb begin
        mult1 = sample_in * coeff1;
        mult2 = temp1 * coeff2;
        mult3 = temp2 * coeff3;
        mult4 = temp3 * coeff4;
        sum = mult1 + mult2 + mult3 + mult4;
    end

    always_ff @(posedge clk) begin
        if(enable==1) begin
            acc_out <= sum;
            temp1 <= sample_in;
            temp2 <= temp1;
            temp3 <= temp2;
            sample_out <= temp3;
        end
    end

endmodule