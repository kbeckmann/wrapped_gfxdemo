`default_nettype none

`timescale 1 ns / 1 ps

module gfxdemo_tb ();

    wire clk;
    wire clk_shift;
    wire rst;

    gfxdemo gfxdemo_0(
        .clk        (clk),
        .reset      (rst),
        .shift_clk  (shift_clk)
    );

endmodule

module dump();
    initial begin
        $dumpfile ("gfxdemo.vcd");
        $dumpvars (0, gfxdemo);
        #1;
    end
endmodule
