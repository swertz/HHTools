#! /bin/env python

from __future__ import division

import argparse
import os
import sys
from array import array

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
    event_weight_sum = sample.event_weight_sum
    cross_section = sample.source_dataset.xsection
    entries = sample.nevents

output = "dy_flavor_fraction.root"

### 161218, 7 var + (real) ht, bb && cc vs. rest
#binning = np.asarray([-0.37849545503700767, -0.252662010953846, -0.21699735110544804, -0.19021412069054136, -0.171396453995042, -0.15676306613552415, -0.14321969667988593, -0.13153891023683148, -0.12107244096732181, -0.11105252860752612, -0.10194490420798973, -0.09332335631432828, -0.08536327877224573, -0.07801048636166992, -0.07120394344115692, -0.0647847651486761, -0.05993005923356425, -0.05408124411388808, -0.04856654729070964, -0.0428596004319479, -0.037361529766591905, -0.03188497839059719, -0.026731425996404594, -0.0216053159528186, -0.016547999887674154, -0.011556509911378651, -0.006637505166127072, -0.001911041855971231, 0.003017405742272187, 0.0076999820179795425, 0.012357098641527476, 0.017143242487650923, 0.021887924437848254, 0.026634181970421666, 0.03165959325886574, 0.03665486332869056, 0.04151823848231689, 0.04651083716266224, 0.051682726965222574, 0.056882360974048966, 0.06180807445815208, 0.06784876065619697, 0.07411968400707587, 0.08150640870709099, 0.09007916053735501, 0.10047784040389708, 0.11391604713844385, 0.12992068221277847, 0.1513985908285126, 0.18121531860439136, 0.3786900843132766],
#        dtype='float')
#binning = np.linspace(-0.38, 0.38, 25)

### 161220, 10 var
# 30 bins
binning = np.asarray([-0.4325139551124535, -0.2146539640268055, -0.17684879232551598, -0.1522156780133781, -0.13344360493544538, -0.1177783085968212, -0.10431773748076387, -0.09240803627202236, -0.08144732988778663, -0.07139562851774808, -0.06195872754019471, -0.053149265226606804, -0.044689436819594426, -0.036486494035769285, -0.028370020384749492, -0.02052289170780913, -0.01265119174726717, -0.004810595256756055, 0.003258152851774066, 0.01125285685430063, 0.019322492143167114, 0.02785483333896287, 0.03659553016370119, 0.04591206104108278, 0.05601279709011762, 0.06690819726322504, 0.07861467402378061, 0.09302953795299788, 0.11151410228370977, 0.13829367256021688, 0.333748766143408],
        dtype='float')

n_bins = len(binning) - 1

flavors = ["b", "c", "l"]

efficiencies = {}

for flav1 in flavors:
    for flav2 in flavors:
        name = "%s%s_frac" % (flav1, flav2)

        frac = ROOT.TEfficiency(name, name, n_bins, binning)
        frac.SetStatisticOption(ROOT.TEfficiency.kMidP)
        frac.SetUseWeightedEvents()
        # Set global weight for sample
        frac.SetWeight(cross_section / event_wgt_sum)

        key = (flav1, flav2)
        efficiencies[key] = frac

chain = ROOT.TChain('t')
for f in files:
    chain.Add(f)

ROOT.TH1.SetDefaultSumw2(True)

chain.SetBranchStatus("*", 0)

chain.SetBranchStatus("hh_jets*", 1)
chain.SetBranchStatus("hh_leptons*", 1)
chain.SetBranchStatus("hh_llmetjj_HWWleptons_nobtag_cmva*", 1)
chain.SetBranchStatus("event_weight", 1)
chain.SetBranchStatus("event_pu_weight", 1)
chain.SetBranchStatus("hh_nJetsL", 1)

bdt_tmva_variables = [
    ( "jet1_p4.Pt()", "jet1_pt" ),
    ( "jet1_p4.Eta()", "jet1_eta" ),
    ( "jet2_p4.Pt()", "jet2_pt" ),
    ( "jet2_p4.Eta()", "jet2_eta" ),
    ( "jj_p4.Pt()", "jj_pt" ),
    ( "ll_p4.Pt()", "ll_pt" ),
    ( "ll_p4.Eta()", "ll_eta" ),
    ( "DPhi_ll_met", "llmetjj_DPhi_ll_met" ),
    ( "ht", "ht" ),
    ( "nJetsL", "nJetsL" ),
]
#bdt_label = "2016_12_18_BDTDY_bb_cc_vs_rest_7var_ht_nJets"
bdt_label = "2016_12_20_BDTDY_bb_cc_vs_rest_10var"
bdt_xml_file = "/home/fynu/swertz/scratch/CMSSW_8_0_25/src/cp3_llbb/HHTools/DYEstimation/weights/{}_kBDT.weights.xml".format(bdt_label)

dict_tmva_variables = { var[1]: array('f', [0]) for var in bdt_tmva_variables }
m_reader = ROOT.TMVA.Reader("Silent=1")
for var in bdt_tmva_variables:
    m_reader.AddVariable(var[1], dict_tmva_variables[var[1]])
m_reader.BookMVA(bdt_label, bdt_xml_file)

print("Loading chain...")
if not entries:
    entries = chain.GetEntries()
print("Done.")

print("Computing jet flavor fraction using %d events." % entries)

for i in range(0, entries):
    chain.GetEntry(i)

    if (i % 100 == 0):
        print("Event %d over %d" % (i + 1, entries))

    hh_jets = chain.hh_jets
    hh_leptons = chain.hh_leptons
    hh_llmetjj_HWWleptons_nobtag_cmva = chain.hh_llmetjj_HWWleptons_nobtag_cmva[0]

    if not (hh_llmetjj_HWWleptons_nobtag_cmva.isElEl or hh_llmetjj_HWWleptons_nobtag_cmva.isMuMu):
        continue

    if (hh_llmetjj_HWWleptons_nobtag_cmva.ll_p4.M() <= 12):
        continue

    # Weight: take into account? Also lepton ID SF?
    weight = chain.event_weight * chain.event_pu_weight * hh_llmetjj_HWWleptons_nobtag_cmva.trigger_efficiency

    def pass_flavor_cut(flav1, flav2):
        return getattr(hh_jets[hh_llmetjj_HWWleptons_nobtag_cmva.ijet1], 'gen_%s' % flav1) and getattr(hh_jets[hh_llmetjj_HWWleptons_nobtag_cmva.ijet2], 'gen_%s' % flav2)

    def get_ht():
        ht = 0
        for jet in hh_jets:
            ht += jet.p4.Pt()
        for lep in hh_leptons:
            ht += lep.p4.pt()
        return ht

    def get_value(object, val):
        if not '()' in val:
            return getattr(object, val)
        else:
            # If 'val' contains an object method, we have to extract the actual method:
            method = val.split(".")[-1].strip("()")
            new_object = getattr(object, ".".join(val.split(".")[:-1]))
            return getattr(new_object, method)()

    for var in bdt_tmva_variables:
        # Special treatment for variables not retrieved from the base object
        if var[0] == "ht":
            dict_tmva_variables["ht"][0] = get_ht()
        elif var[0] == "DPhi_ll_met":
            dict_tmva_variables[var[1]][0] = abs(hh_llmetjj_HWWleptons_nobtag_cmva.DPhi_ll_met)
        elif var[0] == "nJetsL":
            dict_tmva_variables["nJetsL"][0] = chain.hh_nJetsL
        else:
            dict_tmva_variables[var[1]][0] = get_value(hh_llmetjj_HWWleptons_nobtag_cmva, var[0])

    bdt_value = m_reader.EvaluateMVA(bdt_label)

    for flav1 in flavors:
        for flav2 in flavors:
            key = (flav1, flav2)
            efficiencies[key].FillWeighted(pass_flavor_cut(flav1, flav2), weight, bdt_value)

print("Done")
output = ROOT.TFile.Open(output, "recreate")

for key, value in efficiencies.items():
    value.Write()

output.Close()
