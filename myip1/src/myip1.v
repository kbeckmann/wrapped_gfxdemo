`default_nettype none
`timescale 1ns/1ns
module myip1 (
    input clk,
    input reset,
    input enc0_a,
    input enc0_b,
    input enc1_a,
    input enc1_b,
    input enc2_a,
    input enc2_b,
    output pwm0_out,
    output pwm1_out,
    output pwm2_out
);
    reg pwm0_out_r;
    reg pwm1_out_r;
    reg pwm2_out_r;

    assign pwm0_out = pwm0_out_r;
    assign pwm1_out = pwm1_out_r;
    assign pwm2_out = pwm2_out_r;

    always @(posedge clk) begin
        pwm0_out_r <= enc0_a;
        pwm1_out_r <= enc1_a;
        pwm2_out_r <= enc2_a;
    end

endmodule
