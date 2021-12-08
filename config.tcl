# User config
set script_dir [file dirname [file normalize [info script]]]

set ::env(DESIGN_NAME) wrapped_gfxdemo

# Change if needed
set ::env(VERILOG_FILES) "$::env(DESIGN_DIR)/wrapper.v \
    $::env(DESIGN_DIR)/gfxdemo/src/gfxdemo.v"

set ::env(PL_TARGET_DENSITY) 0.40
set ::env(DIE_AREA) "0 0 400 400"
set ::env(FP_SIZING) absolute

set ::env(SYNTH_DEFINES) "MPRJ_IO_PADS=38"

# Setup primary clock to run at max 100MHz (we need 25MHz)
set ::env(CLOCK_PERIOD) "30"
set ::env(CLOCK_PORT) "wb_clk_i"

set ::env(DESIGN_IS_CORE) 0
set ::env(GLB_RT_MAXLAYER) 5

# set ::env(DIODE_INSERTION_STRATEGY) "3"


set ::env(VDD_NETS) [list {vccd1}]
set ::env(GND_NETS) [list {vssd1}]

set ::env(FP_PIN_ORDER_CFG) $script_dir/pin_order.cfg

set ::env(RUN_CVC) 0

# stop OpenLANE from inserting clock buffers, makes tristate problematic
set ::env(PL_RESIZER_BUFFER_OUTPUT_PORTS) 0


# ******************************************************************
# ** Code for shimming SDC file to allow for 2nd clock constraint **
# ******************************************************************
# Setup secondary clock to run at max 250MHz (we need both edges of 125MHz)
# clock2 period is ns
set ::env(CLOCK2_PERIOD) "4"
set ::env(CLOCK2_PORT) "user_clock2"

set ::env(BASE_SDC_FILE_SHIM) "$::env(DESIGN_DIR)/shim.sdc"

# for some reason this gets sourced multiple times so we need to grab original base.sdc only when it doesn't match our shim
if {! [string match $::env(BASE_SDC_FILE) $::env(BASE_SDC_FILE_SHIM)]} {
    set ::env(BASE_SDC_FILE_OLD) $::env(BASE_SDC_FILE)
}

set ::env(BASE_SDC_FILE) $::env(BASE_SDC_FILE_SHIM)

# fix for hold violation
set ::env(PL_RESIZER_HOLD_SLACK_MARGIN) 0.8
set ::env(GLB_RESIZER_HOLD_SLACK_MARGIN) 0.8

