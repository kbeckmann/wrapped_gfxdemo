from types import SimpleNamespace
from nmigen import *
from nmigen.cli import main_parser, main_runner
from nmigen.lib.fifo import SyncFIFOBuffered
from nmigen.lib.cdc import ResetSynchronizer

from random import randint

from pergola.applets.gfxdemo import GFXDemo

from pergola.gateware.tmds import TMDSEncoder
from pergola.gateware.vga import VGAOutput, VGAOutputSubtarget, VGAParameters
from pergola.gateware.vga2dvid import VGA2DVID
from pergola.gateware.vga_testimage import TestImageGenerator, RotozoomImageGenerator




class DVIDParameters():
    def __init__(self, vga_parameters, pll1_freq_mhz, pixel_freq_mhz):
        self.vga_parameters = vga_parameters
        self.pll1_freq_mhz = pll1_freq_mhz
        self.pixel_freq_mhz = pixel_freq_mhz

    def __repr__(self):
        return "(DVIDParameters ({}) {})".format(
            self.vga_parameters,
            self.pll1_freq_mhz,
            self.pixel_freq_mhz)

dvid_configs = {
    "640x480p60": DVIDParameters(VGAParameters(
            h_front=16,
            h_sync=96,
            h_back=44,
            h_active=640,
            v_front=10,
            v_sync=2,
            v_back=31,
            v_active=480,
        ), 100, 25),

    # This uses a clock that is compatible with xdr=7
    "640x480p60_7": DVIDParameters(VGAParameters(
            h_front=16,
            h_sync=96,
            h_back=44,
            h_active=640,
            v_front=10,
            v_sync=2,
            v_back=31,
            v_active=480,
        ), 100, 28),

    "1280x720p60": DVIDParameters(VGAParameters(
            h_front=82,
            h_sync=80,
            h_back=202,
            h_active=1280,
            v_front=3,
            v_sync=5,
            v_back=22,
            v_active=720,
        ), 100, 74),

    # This uses a clock that is compatible with xdr=7
    "1280x720p60_7": DVIDParameters(VGAParameters(
            h_front=82,
            h_sync=80,
            h_back=202,
            h_active=1280,
            v_front=3,
            v_sync=5,
            v_back=22,
            v_active=720,
        ), 100, 70),

    "1920x1080p30": DVIDParameters(VGAParameters(
            h_front=80,
            h_sync=44,
            h_back=148,
            h_active=1920,
            v_front=4,
            v_sync=5,
            v_back=36,
            v_active=1080,
        ), 100, 74),

    # This uses a clock that is compatible with xdr=7
    "1920x1080p30_7": DVIDParameters(VGAParameters(
            h_front=100,
            h_sync=44,
            h_back=215,
            h_active=1920,
            v_front=4,
            v_sync=5,
            v_back=36,
            v_active=1080,
        ), 100, 77),

    # Should be 148.5 MHz but the PLL can't generate 742.5 MHz.
    "1920x1080p60": DVIDParameters(VGAParameters(
            h_front=88,
            h_sync=44,
            h_back=148,
            h_active=1920,
            v_front=4,
            v_sync=5,
            v_back=36,
            v_active=1080,
        ), 100, 150),

    "2560x1440p30": DVIDParameters(VGAParameters(
            h_front=48,
            h_sync=32,
            h_back=80,
            h_active=2560,
            v_front=3,
            v_sync=5,
            v_back=33,
            v_active=1440,
        ), 100, 122),

    # Generates a 60Hz signal but needs 1.2V on VCC.
    # Needs a simpler test image to meet timing on the sync/pixel cd.
    # Can run at 205MHz@1.1V
    "2560x1440p60": DVIDParameters(VGAParameters(
            h_front=20,
            h_sync=20,
            h_back=20,
            h_active=2560,
            v_front=3,
            v_sync=5,
            v_back=5,
            v_active=1440,
        ), 100, 228),
}


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
    buf_io_out = Signal(9)

    buf_irq = Signal(3)

    # Fake differential signals
    m.d.comb += [
        buf_io_out[0].eq( dvid_out_clk),
        buf_io_out[1].eq(~dvid_out_clk),

        buf_io_out[2].eq( dvid_out[0]),
        buf_io_out[3].eq(~dvid_out[0]),

        buf_io_out[4].eq( dvid_out[1]),
        buf_io_out[5].eq(~dvid_out[1]),

        buf_io_out[6].eq( dvid_out[2]),
        buf_io_out[7].eq(~dvid_out[2]),

        buf_io_out[8].eq(pdm_out),

        buf_irq.eq(gfxdemo.irq),
    ]

    wb = gfxdemo.wb
    sel = Signal(4)

    with m.If(sel != 0):
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
        wb.sel,
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
