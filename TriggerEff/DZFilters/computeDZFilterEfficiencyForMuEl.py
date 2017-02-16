#! /bin/env python

import argparse
import os
import struct
import sys
import re

import numpy as np

CMSSW_BASE = os.environ['CMSSW_BASE']
SCRAM_ARCH = os.environ['SCRAM_ARCH']
sys.path.append(os.path.join(CMSSW_BASE, 'bin', SCRAM_ARCH))

# Add default ingrid storm package
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/storm-0.20-py2.7-linux-x86_64.egg')
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/MySQL_python-1.2.3-py2.7-linux-x86_64.egg')

from SAMADhi import Dataset, Sample, File, DbStore

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.Reset()

parser = argparse.ArgumentParser(description='Compute efficiency of DZ filter on MuonEG data samples, by running on events where both versions are present: AND/noDZ gives efficiency')
parser.add_argument('-i', '--id', nargs='+', type=int, metavar='ID', help='Sample ID', required=True)

options = parser.parse_args()

def get_sample(id=None, name=None):
    store = DbStore()
    if (id):
        result = store.find(Sample, Sample.sample_id == id)
    else:
        result = store.find(Sample, Sample.name == unicode(name))

    return result.one()

files = []
storage_root = '/storage/data/cms'
for id in options.id:
    sample = get_sample(id)
    for file in sample.files:
        files.append(storage_root + file.lfn)

files = files#[0:10]

chain = ROOT.TChain('t')
for f in files:
    chain.Add(f)

chain.SetBranchStatus("*", 0)

chain.SetBranchStatus("event_run", 1)
chain.SetBranchStatus("hlt_paths*", 1)

triggers = {
        "MuEl": {
            "re_nodz": re.compile(r"HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v.*"),
            "re_dz": re.compile(r"HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v.*"),
        },
        "ElMu": {
            "re_nodz": re.compile(r"HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v.*"),
            "re_dz": re.compile(r"HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v.*")
        }
    }

for trig in triggers.values():
    trig["n_or"] = 0
    trig["n_nodz"] = 0
    trig["n_and"] = 0

total_entries = chain.GetEntries()
count = 0

for event in chain:
    # DZ versions not present before this run
    if event.event_run < 278273:
        continue

    passed_nodz = {}
    passed_dz = {}
    for trig in triggers.keys():
        passed_nodz[trig] = False
        passed_dz[trig] = False

    for path in event.hlt_paths:
        for trig in triggers.keys():
            if triggers[trig]["re_nodz"].match(path):
                passed_nodz[trig] = True
            if triggers[trig]["re_dz"].match(path):
                passed_dz[trig] = True

    for trig in triggers.keys():
        if passed_nodz[trig]:
            triggers[trig]["n_nodz"] += 1
            
        if passed_nodz[trig] and passed_dz[trig]:
            triggers[trig]["n_and"] += 1

        if passed_nodz[trig] or passed_dz[trig]:
            triggers[trig]["n_or"] += 1

    count += 1

    if count % 10000 == 0:
        print("Processing entry {}".format(count))


print("\n-- Summary --\n")
for trig in triggers.keys():
    print("\t -- Category {} -- ".format(trig))
    try:
        print("Total OR check           : {}".format(triggers[trig]["n_or"]))
        print("Triggered entries        : {}".format(triggers[trig]["n_nodz"]))
        print("Triggered entries with DZ: {}".format(triggers[trig]["n_and"]))
        print("DZ efficiency            : {}\n".format(float(triggers[trig]["n_and"])/triggers[trig]["n_nodz"]))
    except ZeroDivisionError:
        print("Error: tried to divide by zero!!")
print("\nTotal entries check      : {}".format(total_entries))
