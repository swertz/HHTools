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

parser = argparse.ArgumentParser(description='Count number of selected events passing HLT paths')
parser.add_argument('--begin', type=int, help='First run to consider (included)', default=0)
parser.add_argument('--end', type=int, help='Last run to consider (included)', default=1000000)
parser.add_argument('--path', type=str, help='Regexp for the paths to consider', required=True)
parser.add_argument('--samples', type=str, help='Regexp to select samples', required=True)

options = parser.parse_args()

def get_samples(name):
    store = DbStore()
    results = store.find(Sample, Sample.name.like(unicode(name.replace('*', '%'))))

    if results.count() == 0:
        raise Exception("Could not find any sample matching {}".format(name))

    print("Found samples: ")
    for sample in results:
        print(sample.name)

    return results

files = []
storage_root = '/storage/data/cms'
for sample in get_samples(options.samples):
    for file in sample.files:
        files.append(storage_root + file.lfn)

files = files#[0:10]

chain = ROOT.TChain('t')
for f in files:
    chain.Add(f)

chain.SetBranchStatus("*", 0)

chain.SetBranchStatus("event_run", 1)
chain.SetBranchStatus("hlt_paths*", 1)

trigger = re.compile(options.path)

total_entries = chain.GetEntries()
count_passed = 0
count_range = 0
count = 0

for event in chain:
    count += 1

    if event.event_run < options.begin or event.event_run > options.end:
        continue

    count_range += 1

    for path in event.hlt_paths:
        if trigger.match(path):
            count_passed += 1
            break

    if count % 10000 == 0:
        print("Processing entry {} out of {}".format(count, total_entries))


print("\n-- Summary --\n")
print("Total entries in files: {}".format(total_entries))
print("Total entries in range: {}".format(count_range))
print("Entries passing trigger: {}".format(count_passed))
