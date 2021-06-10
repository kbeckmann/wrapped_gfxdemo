from nmigen import *
from nmigen.cli import main_parser, main_runner

from nmigen.hdl.rec import Direction

from random import randint

MPRJ_BASE_ADR = 0x3000_0000


import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    m = Module()

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

    mem = Memory(width=32, depth=128, init=[randint(0, 2**32 - 1) for x in range(128)])
    m.submodules.mem_rd = mem_rd = mem.read_port()

    m.d.comb += mem_rd.addr.eq(wb.adr[2:10])

    ack_r = Signal()

    with m.If(wb.stb & wb.cyc & (wb.adr[10:] == (MPRJ_BASE_ADR >> 10))):
        m.d.comb += wb.dat_r.eq(mem_rd.data)
        m.d.sync += wb.ack.eq(ack_r)
        m.d.sync += ack_r.eq(0)
    with m.Else():
        m.d.sync += ack_r.eq(1)







    reset = Signal()
    m.d.comb += ResetSignal().eq(reset)

    sel = Signal(4)

    shift_clk = Signal()
    buf_io_out = Signal()
    buf_irq = Signal()

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

        shift_clk,

        buf_io_out,

        buf_irq,
    ])
