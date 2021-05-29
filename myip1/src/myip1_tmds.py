from nmigen import *
from nmigen.cli import main_parser, main_runner
from nmigen.lib.fifo import SyncFIFOBuffered

from random import randint

from pergola.gateware.tmds import TMDSEncoder
from pergola.gateware.vga import VGAOutput, VGAOutputSubtarget, VGAParameters
from pergola.gateware.vga2dvid import VGA2DVID
from pergola.gateware.vga_testimage import StaticTestImageGenerator




class DVIDSignalGenerator(Elaboratable):
    def __init__(self, dvid_out_clk, dvid_out, vga_parameters):
        self.dvid_out_clk = dvid_out_clk
        self.dvid_out = dvid_out
        self.vga_parameters = vga_parameters

    def elaborate(self, platform):
        m = Module()

        vga_output = Record([
            ('hs', 1),
            ('vs', 1),
            ('blank', 1),
        ])

        r = Signal(8)
        g = Signal(8)
        b = Signal(8)

        pixel_r = Signal()
        pixel_g = Signal()
        pixel_b = Signal()
        pixel_clk = Signal()

        m.submodules.vga = VGAOutputSubtarget(
            output=vga_output,
            vga_parameters=self.vga_parameters,
        )

        m.submodules.vga2dvid = VGA2DVID(
            in_r = r,
            in_g = g,
            in_b = b,
            in_blank = vga_output.blank,
            in_hsync = vga_output.hs,
            in_vsync = vga_output.vs,
            in_c1 = Const(0, 2),
            in_c2 = Const(0, 2),
            out_r = pixel_r,
            out_g = pixel_g,
            out_b = pixel_b,
            out_clock = pixel_clk,
        )

        # m.submodules += TestImageGenerator(
        m.submodules += StaticTestImageGenerator(
            vsync=vga_output.vs,
            h_ctr=m.submodules.vga.h_ctr,
            v_ctr=m.submodules.vga.v_ctr,
            r=r,
            g=g,
            b=b)

        # Store output bits in separate registers
        #
        # Also invert signals based on parameters
        pixel_clk_r = Signal()
        pixel_r_r = Signal()
        pixel_g_r = Signal()
        pixel_b_r = Signal()
        m.d.shift += pixel_clk_r.eq(pixel_clk)
        m.d.shift += pixel_r_r  .eq(pixel_r)
        m.d.shift += pixel_g_r  .eq(pixel_g)
        m.d.shift += pixel_b_r  .eq(pixel_b)

        m.d.comb += [
            self.dvid_out_clk.eq(pixel_clk_r[0]),
            self.dvid_out.eq(Cat(pixel_b_r[0], pixel_g_r[0], pixel_r_r[0])),
        ]

        return m


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

class ROM(Elaboratable):
    def __init__(self, data, width=8):
        assert type(data) == list

        self.width = width
        self.rom = data

        self.addr = Signal(range(len(data)))
        self.data = Signal(width)

    def elaborate(self, platform):
        m = Module()

        with m.Switch(self.addr):
            for i, word in enumerate(self.rom):
                with m.Case(i):
                    m.d.comb += self.data.eq(word)
            with m.Default():
                m.d.comb += self.data.eq(0)

        return m



if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    m = Module()

    # in
    data = Signal(8)
    c = Signal(2)
    blank = Signal()

    # out
    dvid_out_clk = Signal()
    dvid_out = Signal(3)

    # # Really ugly. Create a fake pixel clock that runs at 1/10 of the sync clock
    # pixel_ctr = Signal(4)
    # pixel_clk = Signal()
    # with m.If(pixel_ctr == 5):
    #     m.d.sync += pixel_ctr.eq(0)
    #     m.d.sync += pixel_clk.eq(~pixel_clk)
    # with m.Else():
    #     m.d.sync += pixel_ctr.eq(pixel_ctr + 1)

    # m.domains += ClockDomain("pixel")
    # m.d.comb += ClockSignal("pixel").eq(pixel_clk)

    # dvid_config = dvid_configs["640x480p60"]
    # m.submodules.dvid_signal_generator = DomainRenamer({"sync": "pixel", "shift": "sync"})(DVIDSignalGenerator(
    #     dvid_out_clk=dvid_out_clk,
    #     dvid_out=dvid_out,
    #     vga_parameters=dvid_config.vga_parameters,
    # ))


    mem_data = Signal(8)
    mem_addr = Signal(16)

    # m.submodules.rom = rom = ROM(width=8, data=[randint(0, 255) for _ in range(256)])
    # m.d.comb += [
    #     rom.addr.eq(mem_addr),
    #     mem_data.eq(rom.data),
    # ]

    mem = Memory(width=8, depth=2048, init=[randint(0, 31) for _ in range(2048)])
    m.submodules.mem_rd = mem_rd = mem.read_port()
    m.d.comb += [
        mem_rd.addr.eq(mem_addr),
        mem_data.eq(mem_rd.data),
    ]

    reset = Signal()
    m.d.sync += ResetSignal().eq(reset)
    m.d.sync += dvid_out.eq(~dvid_out)

    # python myip1_tmds.py generate -t v > myip1.v
    main_runner(parser, args, m, name="myip1", ports=[
        # reset -> rst
        reset,

        # in

        # out
        dvid_out_clk,
        dvid_out,

        mem_addr,
        mem_data,
    ])
