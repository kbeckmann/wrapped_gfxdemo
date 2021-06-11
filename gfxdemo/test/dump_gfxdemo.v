module dump();
    initial begin
        $dumpfile ("gfxdemo.vcd");
        $dumpvars (0, gfxdemo);
        #1;
    end
endmodule
