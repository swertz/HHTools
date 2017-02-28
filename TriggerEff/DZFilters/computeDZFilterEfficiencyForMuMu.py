#! /bin/env python

import argparse
import os
import struct
import sys
import re

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

parser = argparse.ArgumentParser(description='Compute efficiency of DZ filter on DoubleMuon data samples, by running on events where both versions are present: AND/noDZ gives efficiency')
parser.add_argument('-i', '--id', nargs='+', type=int, metavar='ID', help='Sample ID', required=True)
parser.add_argument('-o', '--output', help='Output file', required=True)

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
chain.SetBranchStatus("vertex_n", 1)
chain.SetBranchStatus("hlt_paths*", 1)
chain.SetBranchStatus("hh_leptons*", 1)

triggers = {
        "MuMu": {
            "re_nodz": re.compile(r"HLT_Mu17_TrkIsoVVL_(Tk)?Mu8_TrkIsoVVL_v.*"),
            "re_dz": re.compile(r"HLT_Mu17_TrkIsoVVL_(Tk)?Mu8_TrkIsoVVL_DZ_v.*"),
        },
    }

for key, trig in triggers.items():
    trig["n_or"] = 0
    trig["n_nodz"] = 0
    trig["n_and"] = 0
    trig["th_nodz"] = ROOT.TH1F("total_" + key, "efficiency vs. nPV", 30, 0, 60)
    trig["th_and"] = ROOT.TH1F("pass_" + key, "efficiency vs. nPV", 30, 0, 60)

total_entries = chain.GetEntries()
count = 0

print "Total entries in chain: ", total_entries

for event in chain:
    #if event.event_run < 280960:
    #    continue

    if not event.hh_leptons[0].isMu or not event.hh_leptons[1].isMu:
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
            triggers[trig]["th_nodz"].Fill(ord(event.vertex_n))
            
        if passed_nodz[trig] and passed_dz[trig]:
            triggers[trig]["n_and"] += 1
            triggers[trig]["th_and"].Fill(ord(event.vertex_n))

        if passed_nodz[trig] or passed_dz[trig]:
            triggers[trig]["n_or"] += 1

    count += 1

    if count % 10000 == 0:
        print("Processing entry {}".format(count))

tf = ROOT.TFile(options.output, "recreate")

print("\n-- Summary --\n")

for trig in triggers.keys():
    
    print("\t -- Category {} -- ".format(trig))
    
    try:
        print("Total OR check           : {}".format(triggers[trig]["n_or"]))
        print("Triggered entries        : {}".format(triggers[trig]["n_nodz"]))
        print("Triggered entries with DZ: {}".format(triggers[trig]["n_and"]))
        print("DZ efficiency            : {}\n".format(float(triggers[trig]["n_and"]) / triggers[trig]["n_nodz"]))
        
        c = ROOT.TCanvas("c", "c", 500, 500)
        teff = ROOT.TEfficiency(triggers[trig]["th_and"], triggers[trig]["th_nodz"])
        teff.SetStatisticOption(ROOT.TEfficiency.kBUniform)
        teff.SetTitle("Efficiency vs. nPV -- average: {:.2f}%;nPV".format(100. * float(triggers[trig]["n_and"]) / triggers[trig]["n_nodz"]))
        teff.Draw("AP")
        teff.SetLineWidth(2)
        teff.SetLineColor(ROOT.TColor.GetColor("#1f77b4"))
        c.Print(options.output.split(".root")[0] + ".pdf")
        teff.Write("eff_vs_nPV_" + trig)
    
    except ZeroDivisionError:
        print("Error: tried to divide by zero!!")

print("\nTotal entries check      : {}".format(total_entries))

tf.Close()
