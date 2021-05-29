from nmigen import *
from nmigen.cli import main_parser, main_runner
from nmigen_soc import csr
from nmigen_soc.csr.wishbone import *

MPRJ_BASE_ADR = 0x3000_0000


class MockRegister(Elaboratable):
    def __init__(self, name, width):
        self.element = csr.Element(width, "rw", name=name)
        self.r_count = Signal(8)
        self.w_count = Signal(8)
        self.data    = Signal(width)

    def elaborate(self, platform):
        m = Module()

        with m.If(self.element.r_stb):
            m.d.sync += self.r_count.eq(self.r_count + 1)
        m.d.comb += self.element.r_data.eq(self.data)

        with m.If(self.element.w_stb):
            m.d.sync += self.w_count.eq(self.w_count + 1)
            m.d.sync += self.data.eq(self.element.w_data)

        return m

import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    m = Module()

    m.submodules.mux   = mux   = csr.Multiplexer(addr_width=8, data_width=8, alignment=2)
    m.submodules.reg_1 = reg_1 = MockRegister("reg_1", 32)
    mux.add(reg_1.element)
    m.submodules.reg_2 = reg_2 = MockRegister("reg_2", 32)
    mux.add(reg_2.element)
    m.submodules.reg_3 = reg_3 = MockRegister("reg_3", 32)
    mux.add(reg_3.element)
    m.submodules.reg_4 = reg_4 = MockRegister("reg_4", 32)
    mux.add(reg_4.element)

    m.submodules.dec   = dec   = csr.Decoder(addr_width=32, data_width=8, alignment=2)
    dec.add(mux.bus, addr=MPRJ_BASE_ADR)
    m.submodules.dut   = dut   = WishboneCSRBridge(dec.bus, data_width=32)

    for reg in mux._map.all_resources():
        eprint(f"{reg[0].name}: {reg[1][0]:08x} - {(reg[1][1] - 1):08x}")
    
    # quit()

    # import code
    # code.InteractiveConsole(locals=globals()).interact()


    reset = Signal()
    m.d.comb += ResetSignal().eq(reset)

    sel = Signal(4)
    #m.d.comb += dut.wb_bus.sel.eq(sel)
    m.d.comb += dut.wb_bus.sel.eq(1)

    # python myip1.py generate -t v > myip1.v
    main_runner(parser, args, m, name="myip1", ports=[
        # reset -> rst
        reset,

        dut.wb_bus.adr,
        dut.wb_bus.dat_w,
        dut.wb_bus.dat_r,
        dut.wb_bus.sel,
        dut.wb_bus.cyc,
        dut.wb_bus.stb,
        dut.wb_bus.we,
        dut.wb_bus.ack,

        sel,

        reg_1.element.r_stb,
        reg_1.element.w_stb,

    ])
