#! /bin/env python

from cp3_llbb.CommonTools.condorTools import condorSubmitter

samples = [
    # ttbar
    #{'ID': 2562,
    #'files_per_job': 15},
    # dy
    {'ID': 2557,
    'files_per_job': 30},
    {'ID': 2561,
    'files_per_job': 30},
]

jobs = condorSubmitter(samples, "computeBTaggingEfficiency.py", '', '161223_btaggingEfficiencyOnCondor_DY_checkLight')

jobs.setupCondorDirs()
jobs.createCondorFiles()
jobs.submitOnCondor()
