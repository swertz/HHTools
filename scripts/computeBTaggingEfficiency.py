#! /bin/env python

import argparse
import os
import struct
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

cross_section = 0
event_wgt_sum = 0

if options.json:
    import json
    with open(options.json) as f:
        data = json.load(f)
        data = data[data.keys()[0]]
        files = data["files"]
        cross_section = data["cross-section"]
        event_wgt_sum = data["event-weight-sum"]
    entries = None
else:
    storage_root = '/storage/data/cms'
    sample = get_sample(options.id, options.name)
    files = []
    for file in sample.files:
        files.append(storage_root + file.lfn)
    event_wgt_sum = sample.event_weight_sum
    cross_section = sample.source_dataset.xsection
    entries = sample.nevents

output = "btagging_efficiency.root"

#### Quick and dirty: three different ways to bin the efficiencies:
# - 1D vs. Pt in different Eta ranges
# - 1D vs. Pt and vs. Eta, both inclusively
# - 2D vs. Pt and Eta
## => comment or uncomment required sections below!

#### 1D efficiencies

# Vs. Pt in Eta bins
pt_binning = np.asarray([20, 30, 40, 50, 75, 100, 150, 200, 300, 500], dtype='float')
n_pt_bins = len(pt_binning) - 1

eta_binning = [0, 0.6, 1.2, 1.8, 2.4]

flavours = ["b", "c", "light", "g", "dus"]

efficiencies_pt = {}

for f in flavours:
    eff_eta_bins = {}
    
    for bin in range(len(eta_binning) - 1):
        eta_range = (eta_binning[bin], eta_binning[bin+1])
        this_name = "btagging_eff_on_" + f + "_vs_pt_eta_" + str(eta_range)
        this_eff = ROOT.TEfficiency(this_name, this_name, n_pt_bins, pt_binning)
        this_eff.SetStatisticOption(ROOT.TEfficiency.kBUniform)
        this_eff.SetUseWeightedEvents()
        this_eff.SetWeight(cross_section / event_wgt_sum)
        eff_eta_bins[eta_range] = this_eff
    
    efficiencies_pt[f] = eff_eta_bins

# Vs. Pt and and Vs. Eta
#pt_binning = np.asarray([20, 30, 40, 50, 75, 100, 150, 200, 300, 400, 500], dtype='float')
#n_pt_bins = len(pt_binning) - 1
#
#eta_binning = np.linspace(0, 2.4, 11)
#n_eta_bins = len(eta_binning) - 1
#
#flavours = ["b", "c", "light"]
#
#efficiencies_pt = {}
#efficiencies_eta = {}
#
#for f in flavours:
#    this_eff_pt = ROOT.TEfficiency("btagging_eff_on_" + f + "_vs_pt", "btagging_eff_on_" + f + "_vs_pt", n_pt_bins, pt_binning)
#    this_eff_pt.SetStatisticOption(ROOT.TEfficiency.kMidP)
#    this_eff_pt.SetUseWeightedEvents()
#    this_eff_pt.SetWeight(cross_section / event_wgt_sum)
#    efficiencies_pt[f] = this_eff_pt
#
#    this_eff_eta = ROOT.TEfficiency("btagging_eff_on_" + f + "_vs_eta", "btagging_eff_on_" + f + "_vs_eta", n_eta_bins, eta_binning)
#    this_eff_eta.SetStatisticOption(ROOT.TEfficiency.kMidP)
#    this_eff_eta.SetUseWeightedEvents()
#    efficiencies_eta[f] = this_eff_eta

#### 2D efficiencies
#pt_binning = np.asarray([20, 30, 40, 50, 75, 100, 150, 200, 300, 400, 500, 4000], dtype='float')
#n_pt_bins = len(pt_binning) - 1
#
#eta_binning = np.linspace(0, 2.4, 11)
#n_eta_bins = len(eta_binning) - 1
#
#btagging_eff_on_b = ROOT.TEfficiency("btagging_eff_on_b", "btagging_eff_on_b", n_pt_bins, pt_binning, n_eta_bins, eta_binning)
#btagging_eff_on_b.SetStatisticOption(ROOT.TEfficiency.kMidP)
#btagging_eff_on_b.SetUseWeightedEvents()
#btagging_eff_on_b.SetWeight(cross_section / event_wgt_sum)
#
#btagging_eff_on_c = ROOT.TEfficiency("btagging_eff_on_c", "btagging_eff_on_c", n_pt_bins, pt_binning, n_eta_bins, eta_binning)
#btagging_eff_on_c.SetStatisticOption(ROOT.TEfficiency.kMidP)
#btagging_eff_on_c.SetUseWeightedEvents()
#btagging_eff_on_c.SetWeight(cross_section / event_wgt_sum)
#
#mistagging_eff_on_light = ROOT.TEfficiency("mistagging_eff_on_light", "mistagging_eff_on_light", n_pt_bins, pt_binning, n_eta_bins, eta_binning)
#mistagging_eff_on_light.SetStatisticOption(ROOT.TEfficiency.kMidP)
#mistagging_eff_on_light.SetUseWeightedEvents()
#mistagging_eff_on_light.SetWeight(cross_section / event_wgt_sum)

# cMVAv2 Medium WP
btag_cut = 0.4432

chain = ROOT.TChain('t')
for f in files:
    chain.Add(f)

ROOT.TH1.SetDefaultSumw2(True)

chain.SetBranchStatus("*", 0)

chain.SetBranchStatus("jet_p4*", 1)
chain.SetBranchStatus("jet_hadronFlavor*", 1)
chain.SetBranchStatus("jet_partonFlavor*", 1)
chain.SetBranchStatus("jet_pfCombinedMVAV2BJetTags*", 1)
chain.SetBranchStatus("hh_llmetjj_HWWleptons_nobtag_cmva*", 1)
chain.SetBranchStatus("event_weight", 1)
chain.SetBranchStatus("event_pu_weight", 1)

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
    
        # Weight: take into account? Also lepton ID SF?
        weight = chain.event_weight * chain.event_pu_weight * chain.hh_llmetjj_HWWleptons_nobtag_cmva[0].trigger_efficiency
        
        flavor = ord(chain.jet_hadronFlavor[j])
        partonFlavor = abs(struct.unpack('b', chain.jet_partonFlavor[j])[0])

        #### 1D efficiencies
        if flavor == 5:
            flavor = "b"
        elif flavor == 4:
            flavor = "c"
        else:
            flavor = "light"
        
        # Vs. Pt in Eta bins
        def find_bin(eff_dict, eta):
            for bin, eff in eff_dict.items():
                if eta >= bin[0] and eta < bin[1]:
                    return eff
        
        find_bin(efficiencies_pt[flavor], eta).FillWeighted(chain.jet_pfCombinedMVAV2BJetTags[j] > btag_cut, weight, pt)

        if partonFlavor == 21:
            partonFlavor = "g"
        elif partonFlavor == 1 or partonFlavor == 2 or partonFlavor == 3:
            partonFlavor = "dus"
        if isinstance(partonFlavor, str):
            find_bin(efficiencies_pt[partonFlavor], eta).FillWeighted(chain.jet_pfCombinedMVAV2BJetTags[j] > btag_cut, weight, pt)

        # Vs. Pt and Vs. Eta
        #efficiencies_pt[flavor].FillWeighted(chain.jet_pfCombinedMVAV2BJetTags[j] > btag_cut, weight, pt)
        #efficiencies_eta[flavor].FillWeighted(chain.jet_pfCombinedMVAV2BJetTags[j] > btag_cut, weight, eta)

        #### 2D efficiencies
        #object = None

        #if flavor == 5:
        #    object = btagging_eff_on_b
        #elif flavor == 4:
        #    object = btagging_eff_on_c
        #else:
        #    object = mistagging_eff_on_light

        #object.FillWeighted(chain.jet_pfCombinedMVAV2BJetTags[j] > btag_cut, weight, pt, eta)

print("Done")
output = ROOT.TFile.Open(output, "recreate")

## 1D efficiencies
# Vs. Pt in Eta bins
for f in flavours:
    for eff in efficiencies_pt[f].values():
        eff.Write()
# Vs. Pt and Vs. Eta
#for f in flavours:
#    efficiencies_pt[f].Write()
#    efficiencies_eta[f].Write()

## 2D efficiencies
#btagging_eff_on_b.Write()
#btagging_eff_on_c.Write()
#mistagging_eff_on_light.Write()

output.Close()
