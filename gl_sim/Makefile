# cocotb setup
export COCOTB_REDUCED_LOG_FMT=1
MODULE = test_wrapper
TOPLEVEL = wrapped_gfxdemo
LVS_SOURCE = ../gds/wrapped_gfxdemo.lvs.powered.v
VERILOG_SOURCES = wrapped_gfxdemo.lvs.powered.patched.v

COMPILE_ARGS=-I $(PDK_ROOT)/sky130A/ -DMPRJ_IO_PADS=38

IVERILOG_DUMPER=vcd

include $(shell cocotb-config --makefiles)/Makefile.sim

dollar=$

${VERILOG_SOURCES}: ${LVS_SOURCE}
	# Create a file starting with the header
	cat header.v > $@

	# Append the verilog source
	cat $< >> $@

	# Inject dumfile/dumpvars (nasty)
	sed -i '0,/;/{s/;/;\n\n\
	`ifdef COCOTB_SIM\
		initial begin\
			\\${dollar}dumpfile ("wrapper.vcd");\
			\\${dollar}dumpvars (0, wrapped_gfxdemo);\
			#1;\
		end\
	`endif\
	/}' $@

.PHONY: ${VERILOG_SOURCES}

show:
	gtkwave wrapper.vcd wrapper.gtkw
