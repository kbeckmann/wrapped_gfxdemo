module dump();
    initial begin
        $dumpfile ("myip1.vcd");
        $dumpvars (0, myip1);
        #1;
    end
endmodule
