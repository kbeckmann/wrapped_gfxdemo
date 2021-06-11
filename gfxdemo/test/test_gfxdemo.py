import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles

@cocotb.test()
async def test_start(dut):
    clock = Clock(dut.clk, 40, units="ns")
    cocotb.fork(clock.start())

    await ClockCycles(dut.clk, 10)
    dut.reset <= 1

    await ClockCycles(dut.clk, 10)
    dut.reset <= 0

    # wait
    await ClockCycles(dut.clk, 6000)

