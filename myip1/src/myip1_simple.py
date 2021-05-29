from nmigen import *
from nmigen.cli import main_parser, main_runner

if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    m = Module()

    # in
    enc0_a = Signal()
    enc0_b = Signal()
    enc1_a = Signal()
    enc1_b = Signal()
    enc2_a = Signal()
    enc2_b = Signal()

    # out
    pwm0_out = Signal()
    pwm1_out = Signal()
    pwm2_out = Signal()

    m.d.sync += [
        pwm0_out.eq(enc0_a),
        pwm1_out.eq(enc1_a),
        pwm2_out.eq(enc2_a),
    ]

    reset = Signal()
    m.d.comb += ResetSignal().eq(reset)

    # python myip1.py generate -t v > myip1.v
    main_runner(parser, args, m, name="myip1", ports=[
        # reset -> rst
        reset,

        # in
        enc0_a,
        enc0_b,
        enc1_a,
        enc1_b,
        enc2_a,
        enc2_b,

        # out
        pwm0_out,
        pwm1_out,
        pwm2_out,
    ])
