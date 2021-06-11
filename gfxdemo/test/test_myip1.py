import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles

clocks_per_phase = 10

async def reset(dut):
    dut.enc0_a <= 0
    dut.enc0_b <= 0
    dut.enc1_a <= 0
    dut.enc1_b <= 0
    dut.enc2_a <= 0
    dut.enc2_b <= 0
    dut.reset  <= 1

    await ClockCycles(dut.clk, 5)
    dut.reset <= 0
    await ClockCycles(dut.clk, 5)

@cocotb.test()
async def test_all(dut):
    clock = Clock(dut.clk, 10, units="us")

    cocotb.fork(clock.start())

    await ClockCycles(dut.clk, 2)

    await ClockCycles(dut.clk, 200)