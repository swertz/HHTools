#! /bin/env python

from cp3_llbb.CommonTools.condorTools import condorSubmitter

samples = [
    {'ID': 2557,
    'files_per_job': 30},
    {'ID': 2561,
    'files_per_job': 30},
]

jobs = condorSubmitter(samples, "computeFlavorFractionsOnBDT.py", '', '161220_bb_cc_vs_rest_10var_dyFlavorFractionsOnCondor')

jobs.setupCondorDirs()
jobs.createCondorFiles()
jobs.submitOnCondor()
