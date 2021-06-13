import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles

def wb_deassert(dut):
    dut.wbs_adr_i <= 0
    dut.wbs_cyc_i <= 0
    dut.wbs_dat_i <= 0
    dut.wbs_stb_i <= 0
    dut.wbs_sel_i <= 0
    dut.wbs_we_i  <= 0

async def wb_write(dut, address, data):
    dut.wbs_adr_i <= address
    dut.wbs_cyc_i <= 1
    dut.wbs_stb_i <= 1
    dut.wbs_dat_i <= data
    dut.wbs_sel_i <= 0b1111
    dut.wbs_we_i  <= 1
    await ClockCycles(dut.wb_clk_i, 1)
    for _ in range(10):
        if dut.wbs_ack_o:
            break
        await ClockCycles(dut.wb_clk_i, 1)
    wb_deassert(dut)


@cocotb.test()
async def test_tri(dut):
    clock = Clock(dut.wb_clk_i,     1000/25,  units="ns") #  25 MHz
    clock2 = Clock(dut.user_clock2, 1000/125, units="ns") # 125 MHz

    cocotb.fork(clock.start())
    cocotb.fork(clock2.start())

    # Enable power signals
    dut.vccd1 <= 1
    dut.vssd1 <= 0
    dut.vccd2 <= 1
    dut.vssd2 <= 0
    dut.vdda1 <= 1
    dut.vssa1 <= 0
    dut.vdda2 <= 1
    dut.vssa2 <= 0

    dut.active <= 0

    # Strobe the wishbone reset signal
    dut.wb_rst_i <= 1
    await ClockCycles(dut.wb_clk_i, 5)
    dut.wb_rst_i <= 0

    # All signals are initially unkonwn/x
    dut.la_data_in <= 0
    dut.io_in <= 0
    dut.io_oeb <= 0

    # Deassert the bus signals
    wb_deassert(dut)

    await ClockCycles(dut.wb_clk_i, 10)

    # activate project
    dut.active <= 1
    await ClockCycles(dut.wb_clk_i, 10)

    # reset project
    dut.la_data_in <= 1
    await ClockCycles(dut.wb_clk_i, 10)
    dut.la_data_in <= 0
    await ClockCycles(dut.wb_clk_i, 1)

    # Set DAC
    await wb_write(dut, 0x3000_0000, 0x1234)

    # Assert VGA reset
    await wb_write(dut, 0x3000_0004, 0x1)

    # Write pixels to the row buffer
    for addr in range(0x3000_0100, 0x3000_0100 + 10*4, 4):
        await wb_write(dut, addr, addr % 256)

    # Deassert VGA reset
    await wb_write(dut, 0x3000_0004, 0x0)

    await ClockCycles(dut.wb_clk_i, 10000)
