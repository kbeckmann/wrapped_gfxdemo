# Information about your project

This is a template project you can clone and use to take part in the multi project submission to the
Google/Efabless/Skywater shuttle.

The tools that will test and create the aggregated design are here: https://github.com/mattvenn/multi_project_tools

# Project info.yaml

You need to fill in the fields of [info.yaml](info.yaml)

See [here for more information](https://github.com/mattvenn/multi_project_tools/blob/main/docs/project_spec.md)

# Build GDS

```bash
docker run -it -v $OPENLANE_ROOT:/openLANE_flow -v $PWD:/proj -v $PDK_ROOT:$PDK_ROOT -e PDK_ROOT=$PDK_ROOT -u $(id -u $USER):$(id -g $USER) efabless/openlane:current '/bin/bash' '-c' 'cd /proj; /openLANE_flow/flow.tcl -design .'

cp ./runs/24-05_05-38/results/magic/wrapped_myip1.lef ./runs/24-05_05-38/results/lvs/wrapped_myip1.lvs.powered.v ./runs/24-05_05-38/results/magic/wrapped_myip1.gds gds/
```

# License

This project is [licensed under Apache 2](LICENSE)
