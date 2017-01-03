#! /bin/env python

from __future__ import division

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

output = "dy_flavor_fraction.root"

pt_binning = np.asarray([20, 27, 34, 41, 48, 55, 75, 100, 150, 200, 300, 4000], dtype='float')
n_pt_bins = len(pt_binning) - 1

# eta_binning = np.asarray([0., 0.24, 0.48, 0.72, 0.96, 1.2, 1.44, 1.92, 2.4], dtype='float')
eta_binning = np.asarray([0., 2.4], dtype='float')
n_eta_bins = len(eta_binning) - 1

flavors = ["b", "c", "l"]
njets_binning = ["2j", "3j_and_more"]

efficiencies = {}

for flav1 in flavors:
    for flav2 in flavors:
        name = "%s%s_frac" % (flav1, flav2)

        frac = ROOT.TEfficiency(name, name, n_pt_bins, pt_binning, n_pt_bins, pt_binning)
        frac.SetStatisticOption(ROOT.TEfficiency.kMidP)
        frac.SetUseWeightedEvents()

        key = (flav1, flav2)
        efficiencies[key] = frac

        for njets_bin in njets_binning:
            name = "%s%s_%s_frac" % (flav1, flav2, njets_bin)

            frac = ROOT.TEfficiency(name, name, n_pt_bins, pt_binning, n_pt_bins, pt_binning)
            frac.SetStatisticOption(ROOT.TEfficiency.kMidP)
            frac.SetUseWeightedEvents()

            key = (flav1, flav2, njets_bin)
            efficiencies[key] = frac

jet1_b_ratio = ROOT.TEfficiency("jet1_b_ratio", "jet1_b_ratio", n_pt_bins, pt_binning, n_eta_bins, eta_binning)
jet1_b_ratio.SetStatisticOption(ROOT.TEfficiency.kMidP)
jet1_b_ratio.SetUseWeightedEvents()

jet1_c_ratio = ROOT.TEfficiency("jet1_c_ratio", "jet1_c_ratio", n_pt_bins, pt_binning, n_eta_bins, eta_binning)
jet1_c_ratio.SetStatisticOption(ROOT.TEfficiency.kMidP)
jet1_c_ratio.SetUseWeightedEvents()

jet1_l_ratio = ROOT.TEfficiency("jet1_l_ratio", "jet1_l_ratio", n_pt_bins, pt_binning, n_eta_bins, eta_binning)
jet1_l_ratio.SetStatisticOption(ROOT.TEfficiency.kMidP)
jet1_l_ratio.SetUseWeightedEvents()

jet2_b_ratio = ROOT.TEfficiency("jet2_b_ratio", "jet2_b_ratio", n_pt_bins, pt_binning, n_eta_bins, eta_binning)
jet2_b_ratio.SetStatisticOption(ROOT.TEfficiency.kMidP)
jet2_b_ratio.SetUseWeightedEvents()

jet2_c_ratio = ROOT.TEfficiency("jet2_c_ratio", "jet2_c_ratio", n_pt_bins, pt_binning, n_eta_bins, eta_binning)
jet2_c_ratio.SetStatisticOption(ROOT.TEfficiency.kMidP)
jet2_c_ratio.SetUseWeightedEvents()

jet2_l_ratio = ROOT.TEfficiency("jet2_l_ratio", "jet2_l_ratio", n_pt_bins, pt_binning, n_eta_bins, eta_binning)
jet2_l_ratio.SetStatisticOption(ROOT.TEfficiency.kMidP)
jet2_l_ratio.SetUseWeightedEvents()

chain = ROOT.TChain('t')
for f in files:
    chain.Add(f)

ROOT.TH1.SetDefaultSumw2(True)

chain.SetBranchStatus("*", 0)

chain.SetBranchStatus("hh_jets*", 1)
chain.SetBranchStatus("hh_llmetjj_HWWleptons_nobtag_csv*", 1)
chain.SetBranchStatus("event_weight", 1)

jet1_str = "hh_jets[hh_llmetjj_HWWleptons_nobtag_csv[0].ijet1]"
jet2_str = "hh_jets[hh_llmetjj_HWWleptons_nobtag_csv[0].ijet2]"

print("Loading chain...")
if not entries:
    entries = chain.GetEntries()
print("Done.")

print("Computing jet flavor fraction using %d events." % entries)

for i in range(0, entries):
    chain.GetEntry(i)

    if (i % 10000 == 0):
        print("Event %d over %d" % (i + 1, entries))

    hh_jets = chain.hh_jets
    hh_llmetjj_HWWleptons_nobtag_csv = chain.hh_llmetjj_HWWleptons_nobtag_csv

    if (hh_llmetjj_HWWleptons_nobtag_csv[0].ll_p4.M() <= 12):
        continue

    weight = chain.event_weight

    jet1_pt = hh_jets[hh_llmetjj_HWWleptons_nobtag_csv[0].ijet1].p4.Pt()
    jet1_eta = abs(hh_jets[hh_llmetjj_HWWleptons_nobtag_csv[0].ijet1].p4.Eta())

    jet1_b_ratio.FillWeighted(hh_jets[hh_llmetjj_HWWleptons_nobtag_csv[0].ijet1].gen_b, weight, jet1_pt, jet1_eta)
    jet1_c_ratio.FillWeighted(hh_jets[hh_llmetjj_HWWleptons_nobtag_csv[0].ijet1].gen_c, weight, jet1_pt, jet1_eta)
    jet1_l_ratio.FillWeighted(hh_jets[hh_llmetjj_HWWleptons_nobtag_csv[0].ijet1].gen_l, weight, jet1_pt, jet1_eta)

    jet2_pt = hh_jets[hh_llmetjj_HWWleptons_nobtag_csv[0].ijet2].p4.Pt()
    jet2_eta = abs(hh_jets[hh_llmetjj_HWWleptons_nobtag_csv[0].ijet2].p4.Eta())

    jet2_b_ratio.FillWeighted(hh_jets[hh_llmetjj_HWWleptons_nobtag_csv[0].ijet2].gen_b, weight, jet2_pt, jet2_eta)
    jet2_c_ratio.FillWeighted(hh_jets[hh_llmetjj_HWWleptons_nobtag_csv[0].ijet2].gen_c, weight, jet2_pt, jet2_eta)
    jet2_l_ratio.FillWeighted(hh_jets[hh_llmetjj_HWWleptons_nobtag_csv[0].ijet2].gen_l, weight, jet2_pt, jet2_eta)

    def in_njets_bin(bin):
        if bin == "2j":
            return hh_jets.size() == 2
        elif bin == "3j_and_more":
            return hh_jets.size() > 2

        raise Exception("Invalid bin: %s" % bin)

    def pass_flavor_cut(flav1, flav2):
        return getattr(hh_jets[hh_llmetjj_HWWleptons_nobtag_csv[0].ijet1], 'gen_%s' % flav1) and getattr(hh_jets[hh_llmetjj_HWWleptons_nobtag_csv[0].ijet2], 'gen_%s' % flav2)

    for flav1 in flavors:
        for flav2 in flavors:
            key = (flav1, flav2)
            efficiencies[key].FillWeighted(pass_flavor_cut(flav1, flav2), weight, jet1_pt, jet2_pt)

    for njets_bin in njets_binning:
        if not in_njets_bin(njets_bin):
            continue

        for flav1 in flavors:
            for flav2 in flavors:
                key = (flav1, flav2, njets_bin)
                efficiencies[key].FillWeighted(pass_flavor_cut(flav1, flav2), weight, jet1_pt, jet2_pt)

print("Done")
output = ROOT.TFile.Open(output, "recreate")

for key, value in efficiencies.items():
    value.Write()

jet1_b_ratio.Write()
jet1_c_ratio.Write()
jet1_l_ratio.Write()

jet2_b_ratio.Write()
jet2_c_ratio.Write()
jet2_l_ratio.Write()

output.Close()
