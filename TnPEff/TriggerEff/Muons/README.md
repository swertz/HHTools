## Skim T&P trees

`./skimAll.sh`

## Fit efficiencies

From https://twiki.cern.ch/twiki/bin/view/CMS/MuonTagAndProbeTreesRun2#Last_TnP_fitting_recipe

```
cmsrel CMSSW_8_0_25
cd CMSSW_8_0_25/src
git cms-merge-topic HuguesBrun:fittingRecipeForMoriond8025
git clone git@github.com:cms-analysis/MuonAnalysis-TagAndProbe.git  MuonAnalysis/TagAndProbe -b  80X-v5
```

Apply `patch_for_tree_fitting.patch` on top of HEAD and build

```
cmsRun fitTriggerEfficiencies.py
```

You'll probably need to edit the config file to change the path of the input files.
