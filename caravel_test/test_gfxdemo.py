import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles

@cocotb.test()
async def test_start(dut):
    clock = Clock(dut.clk, 40, units="ns")
    cocotb.fork(clock.start())
    
    dut.RSTB <= 0
    dut.power1 <= 0
    dut.power2 <= 0
    dut.power3 <= 0
    dut.power4 <= 0

    await ClockCycles(dut.clk, 8)
    dut.power1 <= 1
    await ClockCycles(dut.clk, 8)
    dut.power2 <= 1
    await ClockCycles(dut.clk, 8)
    dut.power3 <= 1
    await ClockCycles(dut.clk, 8)
    dut.power4 <= 1

    await ClockCycles(dut.clk, 80)
    dut.RSTB <= 1

    # wait for the project to become active
    await RisingEdge(dut.uut.mprj.wrapped_gfxdemo.active)

    # wait for reset to go low
    await FallingEdge(dut.uut.mprj.wrapped_gfxdemo.gfxdemo_0.reset)

    # wait
    await ClockCycles(dut.clk, 6000)


