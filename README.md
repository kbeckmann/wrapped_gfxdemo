# GFXDemo

This is a design for the Google/Efabless/Skywater shuttle [multi project submission](https://github.com/mattvenn/multi_project_tools).

The design has the following features:
- 640x480 VGA signal generator
- DVI-D signal generator (TMDS encoder)
- Wishbone-controlled 1 bpp 320 pixel wide row buffer
- Wishbone-controlled 2 configurable 24bpp colors
- Wishbone-controlled 16 bit 1st order sigma-delta DAC
- IRQ signals when the vga strobe reaches horizontal active end and vsync

## Setting up the environment for nMigen (optional)

```bash
$ virtualenv -p python3 env
$ source env/bin/activate
$ pip install -r requirements.txt

# Build and run simulation in realtime
$ python -m unittest -vc pergola.applets.gfxdemo.DVIDSim.test_dvid_cxxrtl

# Build and run on a Pergola FPGA
$ python -m pergola run gfxdemo --xdr 2 --config 640x480p60

# Generate verilog output for gfxdemo (should match what is in the repo, but with different paths)
$ python gfxdemo/src/gfxdemo.py generate -t v > gfxdemo/src/gfxdemo.v

```

The source code for gfxdemo can be found in the [pergola_projects repository](https://github.com/kbeckmann/pergola_projects/blob/master/pergola/applets/gfxdemo/__init__.py).

## Build GDS

```bash
docker run -it -v $OPENLANE_ROOT:/openLANE_flow -v $PWD:/proj -v $PDK_ROOT:$PDK_ROOT -e PDK_ROOT=$PDK_ROOT -u $(id -u $USER):$(id -g $USER) efabless/openlane:v0.15 '/bin/bash' '-c' 'cd /proj; /openLANE_flow/flow.tcl -design .'

cp ./runs/.../results/{magic/wrapped_gfxdemo.{gds,lef},lvs/wrapped_gfxdemo.lvs.powered.v} gds/

```

## Git commits

```
caravel_user_project: mpw-two-c
OpenLANE: v0.15
nmigen @ git+https://github.com/nmigen/nmigen@e974a31022d8ba1ee67bd49c82a11fa7a0a71145
pergola-projects @ git+https://github.com/kbeckmann/pergola_projects@564c1e3a0e4431ad719a0fd9b406661b759ced6e
```

# License

This project is [licensed under Apache 2](LICENSE)

Author: Konrad Beckmann
