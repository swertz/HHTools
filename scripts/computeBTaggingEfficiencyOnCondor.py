#! /bin/env python

from cp3_llbb.CommonTools.condorTools import condorSubmitter

samples = [{
    'ID': 2562,
    'files_per_job': 15
}]

jobs = condorSubmitter(samples, "computeBTaggingEfficiency.py", '', 'btaggingEfficiencyOnCondor')

jobs.setupCondorDirs()
jobs.createCondorFiles()
jobs.submitOnCondor()
