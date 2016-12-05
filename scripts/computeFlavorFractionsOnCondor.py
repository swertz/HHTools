#! /bin/env python

from cp3_llbb.CommonTools.condorTools import condorSubmitter

samples = [
    {'ID': 2245,
    'files_per_job': 30},
    {'ID': 2239,
    'files_per_job': 30},
]

jobs = condorSubmitter(samples, "computeFlavorFractions.py", '', 'dyFlavorFractionsOnCondor')

jobs.setupCondorDirs()
jobs.createCondorFiles()
jobs.submitOnCondor()
