# To set-up the standalone matrix elements:

 - Copy the modified `couplings.py` and `coupling_orders.py` into the model directory
 - In MadGraph, do:
```
import model modTEFT_H_test
generate g g > h h EFT=1 EFT_PHIG=0 QCD=2 [virt=QCD]
add process g g > h h EFT=1 EFT_PHIG=1 QCD^2==2 EFT^2==1 EFT_PHIG^2==1\
 [virt=QCD]
add process g g > h h EFT=1 EFT_PHIG=1 QCD^2==2 EFT^2==2 EFT_PHIG^2==1\
 [virt=QCD]
output standalone pp_hh_all_MV_standalone
```
 - Copy the `makefile` into `SubProcesses`, `rw_para.f` into `Source/MODEL`
 - Run `make` in `Source/MODEL`
 - Copy the files of the `P*` subprocesses into the respective folders
 - In each of the folders, run `make test_wrapper`

The subprocesses correspond to:
 0) Only loop-induced diagrams, i.e. everything not involving OphiG
 1) Interference between loop-induced SM diagrams, and tree-level OphiG diagrams
 2) Interference between loop-induced non-SM diagrams, and tree-level OphiG diagrams
