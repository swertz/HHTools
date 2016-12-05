#! /bin/env python

import argparse
import os
import sys

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

parser = argparse.ArgumentParser(description='Compute b-tagging efficiency on a given sample')
group = parser.add_mutually_exclusive_group(required=True)

group.add_argument('-d', '--json', type=str, metavar='FILE', help='JSON file describing the input')
group.add_argument('-i', '--id', type=int, metavar='ID', help='Sample ID')
group.add_argument('-n', '--name', type=str, metavar='STR', help='Sample name')

parser.add_argument('dummy', type=str, help="Dummy argument for compatibility with condorTools")

options = parser.parse_args()

def get_sample(id=None, name=None):
    store = DbStore()
    if (id):
        result = store.find(Sample, Sample.sample_id == id)
    else:
        result = store.find(Sample, Sample.name == unicode(name))

    return result.one()

if options.json:
    import json
    with open(options.json) as f:
        data = json.load(f)
        data = data[data.keys()[0]]
        files = data["files"]
    entries = None
else:
    storage_root = '/storage/data/cms'
    sample = get_sample(options.id, options.name)
    files = []
    for file in sample.files:
        files.append(storage_root + file.lfn)
    entries = sample.nevents

output = "btagging_efficiency.root"

pt_binning = np.asarray([20, 30, 40, 50, 75, 100, 150, 200, 300, 400, 500, 4000], dtype='float')
n_pt_bins = len(pt_binning) - 1

eta_binning = np.linspace(0, 2.4, 11)
n_eta_bins = len(eta_binning) - 1

btagging_eff_on_b = ROOT.TEfficiency("btagging_eff_on_b", "btagging_eff_on_b", n_pt_bins, pt_binning, n_eta_bins, eta_binning)
# btagging_eff_on_b.SetStatisticOption(ROOT.TEfficiency.kMidP)

btagging_eff_on_c = ROOT.TEfficiency("btagging_eff_on_c", "btagging_eff_on_c", n_pt_bins, pt_binning, n_eta_bins, eta_binning)
# btagging_eff_on_c.SetStatisticOption(ROOT.TEfficiency.kMidP)

mistagging_eff_on_light = ROOT.TEfficiency("mistagging_eff_on_light", "mistagging_eff_on_light", n_pt_bins, pt_binning, n_eta_bins, eta_binning)
# mistagging_eff_on_light.SetStatisticOption(ROOT.TEfficiency.kMidP)

btag_cut = 0.800

chain = ROOT.TChain('t')
for f in files:
    chain.Add(f)

ROOT.TH1.SetDefaultSumw2(True)

chain.SetBranchStatus("*", 0)

chain.SetBranchStatus("jet_p4*", 1)
chain.SetBranchStatus("jet_hadronFlavor*", 1)
chain.SetBranchStatus("jet_pfCombinedInclusiveSecondaryVertexV2BJetTags*", 1)

print("Loading chain...")
if not entries:
    entries = chain.GetEntries()
print("Done.")

print("Computing b-tagging efficiency using %d events." % entries)

for i in range(0, entries):
    chain.GetEntry(i)

    if (i % 10000 == 0):
        print("Event %d over %d" % (i + 1, entries))

    njets = chain.jet_p4.size()

    for j in range(0, njets):
        pt = chain.jet_p4[j].Pt()
        eta = abs(chain.jet_p4[j].Eta())

        if pt < 20:
            continue

        if eta > 2.4:
            continue
        
        flavor = ord(chain.jet_hadronFlavor[j])

        object = None

        if flavor == 5:
            object = btagging_eff_on_b
        elif flavor == 4:
            object = btagging_eff_on_c
        else:
            object = mistagging_eff_on_light

        object.Fill(chain.jet_pfCombinedInclusiveSecondaryVertexV2BJetTags[j] > btag_cut, pt, eta)

print("Done")
output = ROOT.TFile.Open(output, "recreate")

btagging_eff_on_b.Write()
btagging_eff_on_c.Write()
mistagging_eff_on_light.Write()

output.Close()
