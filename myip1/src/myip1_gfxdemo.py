from nmigen import *
from nmigen.cli import main_parser, main_runner
from nmigen.lib.cdc import ResetSynchronizer

from pergola.applets.gfxdemo import GFXDemo
from pergola.applets.gfxdemo import dvid_configs


if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    m = Module()

    # out
    dvid_out_clk = Signal()
    dvid_out = Signal(3)

    # Create a global active high reset signal called `reset`
    reset = Signal()
    m.d.comb += ResetSignal(domain="sync").eq(reset)

    # Create `shift` clockdomain for the fast clock domain (5x pixel clock)
    shift_clk = ClockSignal("shift")
    m.domains += ClockDomain("shift")
    m.submodules += ResetSynchronizer(reset, domain="shift")

    dvid_config = dvid_configs["640x480p60"]

    pdm_out = Signal()
    m.submodules.gfxdemo = gfxdemo = GFXDemo(
        dvid_out=dvid_out,
        dvid_out_clk=dvid_out_clk,
        pdm_out=pdm_out,
        vga_parameters=dvid_config.vga_parameters,
        xdr=2,
        emulate_ddr=True)

    # Raw output signals
    buf_io_out = Signal(16)

    buf_irq = Signal(3)

    m.d.comb += [
        # DVI-D emulated differential signals
        buf_io_out[0].eq( dvid_out_clk),
        buf_io_out[1].eq(~dvid_out_clk),

        buf_io_out[2].eq( dvid_out[0]),
        buf_io_out[3].eq(~dvid_out[0]),

        buf_io_out[4].eq( dvid_out[1]),
        buf_io_out[5].eq(~dvid_out[1]),

        buf_io_out[6].eq( dvid_out[2]),
        buf_io_out[7].eq(~dvid_out[2]),

        # DAC
        buf_io_out[8].eq(pdm_out),

        # VGA signals
        buf_io_out[9].eq(gfxdemo.dvid.vga_output.hs),
        buf_io_out[10].eq(gfxdemo.dvid.vga_output.vs),
        buf_io_out[11].eq(gfxdemo.dvid.r),
        buf_io_out[12].eq(gfxdemo.dvid.g),
        buf_io_out[13].eq(gfxdemo.dvid.b),

        # Clock signals
        buf_io_out[14].eq(ClockSignal("sync")),
        buf_io_out[15].eq(ClockSignal("shift")),

        # IRQ
        buf_irq.eq(gfxdemo.irq),
    ]

    wb = gfxdemo.wb
    sel = Signal(4)

    with m.If(sel == 0b1111):
        m.d.comb += wb.sel.eq(1)

    # python myip1_tmds.py generate -t v > myip1.v
    main_runner(parser, args, m, name="myip1", ports=[
        # reset -> rst
        reset,

        # fast clock input
        shift_clk,

        # wishbone
        wb.adr,
        wb.dat_w,
        wb.dat_r,
        wb.cyc,
        wb.stb,
        wb.we,
        wb.ack,
        sel,

        # in

        # out
        buf_io_out,
        buf_irq,
    ])
