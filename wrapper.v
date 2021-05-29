`default_nettype none
`ifdef FORMAL
    `define MPRJ_IO_PADS 38    
`endif
module wrapped_myip1(
`ifdef USE_POWER_PINS
    inout vdda1,	// User area 1 3.3V supply
    inout vdda2,	// User area 2 3.3V supply
    inout vssa1,	// User area 1 analog ground
    inout vssa2,	// User area 2 analog ground
    inout vccd1,	// User area 1 1.8V supply
    inout vccd2,	// User area 2 1.8v supply
    inout vssd1,	// User area 1 digital ground
    inout vssd2,	// User area 2 digital ground
`endif
    // interface as user_proj_example.v
    input wire wb_clk_i,
    input wire wb_rst_i,
    input wire wbs_stb_i,
    input wire wbs_cyc_i,
    input wire wbs_we_i,
    input wire [3:0] wbs_sel_i,
    input wire [31:0] wbs_dat_i,
    input wire [31:0] wbs_adr_i,
    output wire wbs_ack_o,
    output wire [31:0] wbs_dat_o,

    // Logic Analyzer Signals
    // only provide first 32 bits to reduce wiring congestion
    input  wire [31:0] la_data_in,
    output wire [31:0] la_data_out,
    input  wire [31:0] la_oen,

    // IOs
    input  wire [`MPRJ_IO_PADS-1:0] io_in,
    output wire [`MPRJ_IO_PADS-1:0] io_out,
    output wire [`MPRJ_IO_PADS-1:0] io_oeb,
    
    // active input, only connect tristated outputs if this is high
    input wire active
);

    // all outputs must be tristated before being passed onto the project
    wire buf_wbs_ack_o;
    wire [31:0] buf_wbs_dat_o;
    wire [31:0] buf_la_data_out;
    wire [`MPRJ_IO_PADS-1:0] buf_io_out;
    wire [`MPRJ_IO_PADS-1:0] buf_io_oeb;

    `ifdef FORMAL
    // formal can't deal with z, so set all outputs to 0 if not active
    assign wbs_ack_o    = active ? buf_wbs_ack_o    : 1'b0;
    assign wbs_dat_o    = active ? buf_wbs_dat_o    : 32'b0;
    assign la_data_out  = active ? buf_la_data_out  : 32'b0;
    assign io_out       = active ? buf_io_out       : {`MPRJ_IO_PADS{1'b0}};
    assign io_oeb       = active ? buf_io_oeb       : {`MPRJ_IO_PADS{1'b0}};
    `include "properties.v"
    `else
    // tristate buffers
    assign wbs_ack_o    = active ? buf_wbs_ack_o    : 1'bz;
    assign wbs_dat_o    = active ? buf_wbs_dat_o    : 32'bz;
    assign la_data_out  = active ? buf_la_data_out  : 32'bz;
    assign io_out       = active ? buf_io_out       : {`MPRJ_IO_PADS{1'bz}};
    assign io_oeb       = active ? buf_io_oeb       : {`MPRJ_IO_PADS{1'bz}};
    `endif

    // permanently set oeb so that outputs are always enabled: 0 is output, 1 is high-impedance
    assign buf_io_oeb = {`MPRJ_IO_PADS{1'b0}};

    // instantiate your module here, connecting what you need of the above signals
    // myip1 myip1_0(
    //     .clk        (wb_clk_i),
    //     .reset      (la_data_in[0]),
    //     .enc0_a     (io_in[8]),
    //     .enc0_b     (io_in[9]),
    //     .enc1_a     (io_in[10]),
    //     .enc1_b     (io_in[11]),
    //     .enc2_a     (io_in[12]),
    //     .enc2_b     (io_in[13]),
    //     .pwm0_out   (buf_io_out[14]),
    //     .pwm1_out   (buf_io_out[15]),
    //     .pwm2_out   (buf_io_out[16]));


    // simple test
    // myip1 myip1_0(
    //     .clk        (wb_clk_i),
    //     .reset      (la_data_in[0])
    // );

    // TMDS test
//     myip1 myip1_0(
//         .clk        (wb_clk_i),
//         .reset      (la_data_in[0]),

//         .dvid_out_clk (buf_io_out[0]),
//         .dvid_out     (buf_io_out[3:1]),

// //        .mem_ren      (     io_in[4]),
//         .mem_data     ( buf_io_out[15:8]),
//         .mem_addr     (     io_in[31:16])
//     );

    // GOL test
    myip1 myip1_0(
        .clk        (wb_clk_i),
        .reset      (la_data_in[0]),

        // FIXME: *MUST* route to user_clock2 later!!!
        .shift_clk  (wb_clk_i),

        // Route 8 output pins
        .buf_io_out (buf_io_out[15:8]),

        .wb__adr   (wbs_adr_i),
        .wb__dat_w (wbs_dat_i),
        .wb__dat_r (buf_wbs_dat_o),
        //.wb__sel   (wbs_sel_i),
        .sel       (wbs_sel_i),
        .wb__cyc   (wbs_cyc_i),
        .wb__stb   (wbs_stb_i),
        .wb__we    (wbs_we_i),
        .wb__ack   (buf_wbs_ack_o)
    );

    // WB test
    // myip1 myip1_0(
    //     .clk        (wb_clk_i),
    //     .reset      (la_data_in[0]),

    //     .wb__adr   (wbs_adr_i),
    //     .wb__dat_w (wbs_dat_i),
    //     .wb__dat_r (buf_wbs_dat_o),
    //     //.wb__sel   (wbs_sel_i),
    //     .sel       (wbs_sel_i),
    //     .wb__cyc   (wbs_cyc_i),
    //     .wb__stb   (wbs_stb_i),
    //     .wb__we    (wbs_we_i),
    //     .wb__ack   (buf_wbs_ack_o)
    // );

    // WB test2
    // myip1 myip1_0(
    //     .clk        (wb_clk_i),
    //     .reset      (la_data_in[0]),

    //     .wb__adr   (wbs_adr_i),
    //     .wb__dat_w (wbs_dat_i),
    //     .wb__dat_r (buf_wbs_dat_o),
    //     //.wb__sel   (wbs_sel_i),
    //     .sel       (wbs_sel_i),
    //     .wb__cyc   (wbs_cyc_i),
    //     .wb__stb   (wbs_stb_i),
    //     .wb__we    (wbs_we_i),
    //     .wb__ack   (buf_wbs_ack_o)
    // );

endmodule 
`default_nettype wire
