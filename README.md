# HHTools
Toolbox for resonant HH analysis 

## Setup instructions
This repository consist only of scripts to make interface with the CommonTools and PlotIt facilities. The only thing required before to launch anything is :
```
cms_env
cmenv
```
with 
```
alias cms_env="module purge; module load grid/grid_environment_sl6; module load crab/crab3; module load cms/cmssw;"
```

## Produce TH1(2) out of the output of HHAnalyzer

This step is done in ```histFactory_hh```. You need a python script to generate the plots (such as ```generatePlots.py``` based on ```basePlotter.py```). The important is that this code defines a list called ```plots```. To launch the TH1(2) production, use ```python launchHistFactory.py -o OUTPUTFOLDER -p PLOTTER.PY -s -r```. The ```-s``` option actually submit the jobs on condor, use it first without to check that there is no error with ```source OUTPUTFOLDER/condor/input/condor_1.sh```. The ```-r``` option removes ```OUTPUTFOLDER``` if it exists. NB : to avoid risky command, it first prompts the command, you need to confirm by typing "enter".

## Produce stacked plots with the output of histFactory

This step is done in ```plotIt_hh```.  
