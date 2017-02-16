#!/usr/bin/env python

import csv
import re

# Compute unprescaled lumi for a HLT path using run-by-run granularity
# Path regexp should match ONLY one path, but allow non-overlapping versions of it

# Command for lumi files:
# brilcalc lumi --normtag /afs/cern.ch/user/l/lumipro/public/normtag_file/normtag_DATACERT.json -i Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt -u '/pb' --hltpath 'HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_*' --output csv
# (adapt the HLT path)

# Command for prescale files:
# brilcalc trg --prescale --hltpath 'HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_*' --output csv
# (adapt the HLT path)

#lumi_file = 'brilcalc_MuMu_noDZ.csv'
#prescale_file = 'checkPrescales_MuMu_noDZ.csv'
#path_regex = R"HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v.*"

lumi_file = 'brilcalc_ElMu.csv'
prescale_file = 'checkPrescales_ElMu.csv'
path_regex = R"HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v.*"

#lumi_file = 'brilcalc_MuEl.csv'
#prescale_file = 'checkPrescales_MuEl.csv'
#path_regex = R"HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v.*"

# Each run: path, lumi, prescale
runs = {}

# First find recorded lumi for each run where the path was active
with open(lumi_file) as _f:
    reader = csv.reader(_f)
    for l in reader:
        if len(l) != 6 or l[0] == '' or  l[0][0] == '#':
            continue
        run = l[0].split(":")[0]
        path = l[3]
        lumi = float(l[5])
        if re.match(path_regex, path):
            if run in runs.keys():
                raise Exception("Run {}: two paths... {} and {}".format(run, runs[run][0], path))
            runs[run] = [path, lumi, []]

# Find the prescales for each run for the path
with open(prescale_file) as _f:
    reader = csv.reader(_f)
    for l in reader:
        if len(l) != 7 or l[0] == '' or  l[0][0] == '#':
            continue
        run = l[0]
        path = l[4]
        ps = int(l[3])
        if ps <= 0:
            continue
        if run not in runs.keys():
            continue
        if re.match(path_regex, path):
            if ps not in runs[run][2]:
                runs[run][2].append(ps)

#for r in runs.items():
#    print r

unprescaled_lumi = 0

for i, run in runs.items():
    prescales = run[2]
    if len(prescales) == 1 and prescales[0] == 1:
        unprescaled_lumi += run[1]
    if len(prescales) > 1 and 1 in prescales:
        print "WARNING: run {} has several prescales: {} with lumi: {}".format(i, prescales, run[1])

print "Total unprescaled lumi: {}".format(unprescaled_lumi)
