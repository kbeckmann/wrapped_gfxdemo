from nmigen import *
from nmigen.cli import main_parser, main_runner

from nmigen.hdl.rec import Direction

from buswrapper import BusWrapper

MPRJ_BASE_ADR = 0x3000_0000


import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    m = Module()

    rw0 = Signal(32)
    rw1 = Signal(32)
    rw2 = Signal(32)
    rw3 = Signal(32)

    m.submodules.wrapper = wrapper = BusWrapper(
        signals_r=[rw0, rw1, rw2, rw3],
        signals_w=[rw0, rw1, rw2, rw3],
    )

    eprint(wrapper)

    addr_width = 32
    data_width = 32
    granularity = 32

    layout = [
        ("adr",   addr_width, Direction.FANOUT),
        ("dat_w", data_width, Direction.FANOUT),
        ("dat_r", data_width, Direction.FANIN),
        ("sel",   data_width // granularity, Direction.FANOUT),
        ("cyc",   1, Direction.FANOUT),
        ("stb",   1, Direction.FANOUT),
        ("we",    1, Direction.FANOUT),
        ("ack",   1, Direction.FANIN),
    ]

    wb = Record(layout=layout)

    m.d.comb += wrapper.cs.eq(0)
    m.d.comb += wrapper.we.eq(wb.we)
    m.d.comb += wrapper.addr.eq(wb.adr[2:8])

    ack_r = Signal()

    with m.If(wb.stb & wb.cyc & (wb.adr[8:] == (MPRJ_BASE_ADR >> 8))):
        m.d.comb += wrapper.cs.eq(1)
        m.d.comb += wb.dat_r.eq(wrapper.read_data)
        m.d.comb += wrapper.write_data.eq(wb.dat_w)
        m.d.sync += wb.ack.eq(ack_r)
        m.d.sync += ack_r.eq(0)
    with m.Else():
        m.d.sync += ack_r.eq(1)







    reset = Signal()
    m.d.comb += ResetSignal().eq(reset)

    sel = Signal(4)

    # python myip1.py generate -t v > myip1.v
    main_runner(parser, args, m, name="myip1", ports=[
        # reset -> rst
        reset,

        wb.adr,
        wb.dat_w,
        wb.dat_r,
        wb.sel,
        wb.cyc,
        wb.stb,
        wb.we,
        wb.ack,

        sel,

    ])
