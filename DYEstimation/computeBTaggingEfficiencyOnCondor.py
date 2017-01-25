#! /bin/env python

from cp3_llbb.CommonTools.condorTools import condorSubmitter

samples = [
    # ttbar
    # {'ID': 2999,
    # 'files_per_job': 15},

    # DY
    # 0J
    {'ID': 3007,
    'files_per_job': 30},

    # 1J
    {'ID': 2978,
    'files_per_job': 30},

    # 2J
    {'ID': 2994,
    'files_per_job': 30},

    # M-10to50
    {'ID': 2983,
    'files_per_job': 30},
]

jobs = condorSubmitter(samples, "computeBTaggingEfficiency.py", '', '170125_btaggingEfficiencyOnCondor_new_prod_DY')

jobs.setupCondorDirs()
jobs.createCondorFiles()
jobs.submitOnCondor()
