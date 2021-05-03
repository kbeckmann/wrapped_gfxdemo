# User config
set ::env(DESIGN_NAME) gfxdemo

# Change if needed
set ::env(VERILOG_FILES) [glob $::env(DESIGN_DIR)/src/*.v]

set ::env(PL_TARGET_DENSITY) 0.4
set ::env(FP_CORE_UTIL) 30

# Fill this
set ::env(CLOCK_PERIOD) "1"
set ::env(CLOCK_PORT) "clk"

set filename $::env(DESIGN_DIR)/$::env(PDK)_$::env(STD_CELL_LIBRARY)_config.tcl
if { [file exists $filename] == 1} {
	source $filename
}

