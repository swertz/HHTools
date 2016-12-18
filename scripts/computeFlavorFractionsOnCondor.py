#! /bin/env python

from cp3_llbb.CommonTools.condorTools import condorSubmitter

samples = [
    {'ID': 2245,
    'files_per_job': 30},
    {'ID': 2239,
    'files_per_job': 30},
]

jobs = condorSubmitter(samples, "computeFlavorFractionsOnBDT.py", '', '161214_bb_cc_vs_rest_7var_ht_nJets_dyFlavorFractionsOnCondor')

jobs.setupCondorDirs()
jobs.createCondorFiles()
jobs.submitOnCondor()
