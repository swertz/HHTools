# HHTools
Toolbox for resonant HH analysis

## Setup instructions

This repository consists of scripts interfacing the CommonTools and PlotIt facilities. It does not require any compilation, just follow this instructions below to setup everything.

### First time only

We use Keras and Tensorflow for Neural Network training / evaluation, which is not available in CMSSW. When first installing this repository, you must register an already pre-built version of Keras and Tensorflow by executing the `add_keras_to_cmssw.sh` script at the root of the repository. **Note**: you must first be in a CMSSW environment by doing a `cmsenv`.

### Everytime

```
cms_env
cmsenv
```

with, in the .bashrc,

`alias cms_env="module purge; module load grid/grid_environment_sl6; module load crab/crab3; module load cms/cmssw;"`.

## Produce TH1(2) out of HHAnalyzer output

This step is done in ```histFactory_hh```. You need a python script to generate the plots (such as ```generatePlots.py``` based on ```basePlotter.py```). The important is that this code defines a list called ```plots```. To launch the TH1(2) production, use

```python launchHistFactory.py -o OUTPUTFOLDER -s -r```. 

The ```-s``` option actually submit the jobs on condor, use it first without to check that there is no error with ```source OUTPUTFOLDER/condor/input/condor_1.sh```. The ```-r``` option removes ```OUTPUTFOLDER``` if it exists. NB : to avoid risky command, it first prompts the command, you need to confirm by typing "enter".
 
## Produce stacked plots with the output of histFactory
 
This step is done in ```plotIt_hh```. To launch the plots : 

`./plotIt.sh [SUFFIX]`

will create a folder named `plots_all_DATE_SUFFIX` with all the stacked plots inside, SUFFIX being optional.

Here are the key files you have to modify : 

`centralConfig.yml` : to specify the directory where the rootfiles are.

`listHistos.py` : you can modify the rootFile at the top and run `python listHistos.py` to generate the .yml file with axis labels, blinded range, etc.

`MCFiles.yml` and `DataFiles.yml` to specify the samples you want to run on. Usually you just need to replace the old tag by the new one (e.g. in  vim `:%s/v2.0.3+7415_HHAnalysis_2016-01-30.v3/v2.0.4+7415_HHAnalysis_2016-02-14.v0/`).

`groups.yml` to specify the colors, the names and which samples should appear merged in the legend.
