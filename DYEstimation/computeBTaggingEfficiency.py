#! /bin/env python

import argparse
import os
import struct
import sys
import functools

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

# # Vs. Pt in Eta bins
# pt_binning = np.asarray([20, 30, 40, 50, 75, 100, 150, 200, 300, 500], dtype='float')
# n_pt_bins = len(pt_binning) - 1

# eta_binning = [0, 0.6, 1.2, 1.8, 2.4]

# flavours = ["b", "c", "light", "g", "dus"]

# efficiencies_pt = {}

# for f in flavours:
    # eff_eta_bins = {}

    # for bin in range(len(eta_binning) - 1):
        # eta_range = (eta_binning[bin], eta_binning[bin+1])
        # this_name = "btagging_eff_on_" + f + "_vs_pt_eta_" + str(eta_range)
        # this_eff = ROOT.TEfficiency(this_name, this_name, n_pt_bins, pt_binning)
        # this_eff.SetStatisticOption(ROOT.TEfficiency.kBUniform)
        # this_eff.SetUseWeightedEvents()
        # this_eff.SetWeight(cross_section / event_wgt_sum)
        # eff_eta_bins[eta_range] = this_eff

    # efficiencies_pt[f] = eff_eta_bins

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
pt_binning = np.asarray([20, 30, 40, 50, 75, 100, 150, 200, 300, 400, 500, 4000], dtype='float')
n_pt_bins = len(pt_binning) - 1

eta_binning = np.linspace(0, 2.4, 6)
n_eta_bins = len(eta_binning) - 1

# cMVAv2 Medium WP
btag_cut = 0.4432

chain = ROOT.TChain('t')
for f in files:
    chain.Add(f)

ROOT.TH1.SetDefaultSumw2(True)

chain.SetBranchStatus("*", 0)

chain.SetBranchStatus("jet_*p4*", 1)
chain.SetBranchStatus("jet_*hadronFlavor*", 1)
# chain.SetBranchStatus("jet_*partonFlavor*", 1)
chain.SetBranchStatus("jet_*pfCombinedMVAV2BJetTags*", 1)
# chain.SetBranchStatus("hh_llmetjj_HWWleptons_nobtag_cmva*", 1)
chain.SetBranchStatus("event_weight", 1)
chain.SetBranchStatus("event_pu_weight*", 1)
chain.SetBranchStatus("event_pdf_weight*", 1)
chain.SetBranchStatus("event_scale_weights*", 1)

systematics_list = ['nominal', 'pu', 'pdf', 'jec', 'jer', 'scaleUncorr']

systematics_on_nominal = {
        'nominal': {
            'weight': lambda c: chain.event_weight * chain.event_pu_weight * chain.event_pdf_weight,
            'cut': lambda c: True
            },
        'pdfup': {
            'weight': lambda c: chain.event_weight * chain.event_pu_weight * chain.event_pdf_weight_up,
            'cut': lambda c: True
            },
        'pdfdown': {
            'weight': lambda c: chain.event_weight * chain.event_pu_weight * chain.event_pdf_weight_down,
            'cut': lambda c: True
            },
        'puup': {
            'weight': lambda c: chain.event_weight * chain.event_pu_weight_up * chain.event_pdf_weight,
            'cut': lambda c: True
            },
        'pudown': {
            'weight': lambda c: chain.event_weight * chain.event_pu_weight_down * chain.event_pdf_weight,
            'cut': lambda c: True
            }
        }

for i in range(0, 6):
    systematics_on_nominal['scaleUncorr' + str(i)] = {
            'weight': functools.partial(lambda i, c,: chain.event_weight * chain.event_pu_weight * chain.event_pdf_weight * chain.event_scale_weights[i], i),
            'cut': lambda c: True
    }

systematics_jets = {
        'jecup': {
            'p4': lambda c: c.jet_jecup_p4,
            'flavor': lambda c: c.jet_jecup_hadronFlavor,
            'btag': lambda c: c.jet_jecup_pfCombinedMVAV2BJetTags
            },
        'jecdown': {
            'p4': lambda c: c.jet_jecdown_p4,
            'flavor': lambda c: c.jet_jecdown_hadronFlavor,
            'btag': lambda c: c.jet_jecdown_pfCombinedMVAV2BJetTags
            },
        'jerup': {
            'p4': lambda c: c.jet_jerup_p4,
            'flavor': lambda c: c.jet_jerup_hadronFlavor,
            'btag': lambda c: c.jet_jerup_pfCombinedMVAV2BJetTags
            },
        'jerdown': {
            'p4': lambda c: c.jet_jerdown_p4,
            'flavor': lambda c: c.jet_jerdown_hadronFlavor,
            'btag': lambda c: c.jet_jerdown_pfCombinedMVAV2BJetTags
            },
        }

def create_efficiencies(syst=""):
    if len(syst) > 0:
        syst = "__" + syst

    btagging_eff_on_b = ROOT.TEfficiency("btagging_eff_on_b%s" % syst, "btagging_eff_on_b%s" % syst, n_pt_bins, pt_binning, n_eta_bins, eta_binning)
    btagging_eff_on_b.SetStatisticOption(ROOT.TEfficiency.kBUniform)
    btagging_eff_on_b.SetUseWeightedEvents()
    btagging_eff_on_b.SetWeight(cross_section / event_wgt_sum)

    btagging_eff_on_c = ROOT.TEfficiency("btagging_eff_on_c%s" % syst, "btagging_eff_on_c%s" % syst, n_pt_bins, pt_binning, n_eta_bins, eta_binning)
    btagging_eff_on_c.SetStatisticOption(ROOT.TEfficiency.kBUniform)
    btagging_eff_on_c.SetUseWeightedEvents()
    btagging_eff_on_c.SetWeight(cross_section / event_wgt_sum)

    mistagging_eff_on_light = ROOT.TEfficiency("mistagging_eff_on_light%s" % syst, "mistagging_eff_on_light%s" % syst, n_pt_bins, pt_binning, n_eta_bins, eta_binning)
    mistagging_eff_on_light.SetStatisticOption(ROOT.TEfficiency.kBUniform)
    mistagging_eff_on_light.SetUseWeightedEvents()
    mistagging_eff_on_light.SetWeight(cross_section / event_wgt_sum)

    return (btagging_eff_on_b, btagging_eff_on_c, mistagging_eff_on_light)

btagging_eff_on_b = {}
btagging_eff_on_c = {}
mistagging_eff_on_light = {}

for s in systematics_list:
    if s == 'nominal':
        a, b, c = create_efficiencies()
        btagging_eff_on_b[s] = a
        btagging_eff_on_c[s] = b
        mistagging_eff_on_light[s] = c
    elif s == 'scaleUncorr':
        for i in range(0, 6):
            s_ = s + str(i)
            a, b, c = create_efficiencies(s_)
            btagging_eff_on_b[s_] = a
            btagging_eff_on_c[s_] = b
            mistagging_eff_on_light[s_] = c
    else:
        for v in ['up', 'down']:
            s_ = s + v
            a, b, c = create_efficiencies(s_)
            btagging_eff_on_b[s_] = a
            btagging_eff_on_c[s_] = b
            mistagging_eff_on_light[s_] = c

print("Loading chain...")
if not entries:
    entries = chain.GetEntries()
print("Done.")

print("Computing b-tagging efficiency using %d events." % entries)

for i in range(0, entries):
    chain.GetEntry(i)

    if (i % 10000 == 0):
        print("Event %d over %d" % (i + 1, entries))

    # Nominal jet collection
    njets = chain.jet_p4.size()

    for j in range(0, njets):
        pt = chain.jet_p4[j].Pt()
        eta = abs(chain.jet_p4[j].Eta())

        if pt < 20:
            continue

        if eta > 2.4:
            continue

        flavor = ord(chain.jet_hadronFlavor[j])
        # partonFlavor = abs(struct.unpack('b', chain.jet_partonFlavor[j])[0])

        for s, info in systematics_on_nominal.items():

            if not info['cut'](chain):
                continue

            weight = info['weight'](chain)
            object = None

            #### 1D efficiencies (not updated for systematics!)
            # if flavor == 5:
                # flavor = "b"
            # elif flavor == 4:
                # flavor = "c"
            # else:
                # flavor = "light"

            # # Vs. Pt in Eta bins
            # def find_bin(eff_dict, eta):
                # for bin, eff in eff_dict.items():
                    # if eta >= bin[0] and eta < bin[1]:
                        # return eff

            # find_bin(efficiencies_pt[flavor], eta).FillWeighted(chain.jet_pfCombinedMVAV2BJetTags[j] > btag_cut, weight, pt)

            # if partonFlavor == 21:
                # partonFlavor = "g"
            # elif partonFlavor == 1 or partonFlavor == 2 or partonFlavor == 3:
                # partonFlavor = "dus"
            # if isinstance(partonFlavor, str):
                # find_bin(efficiencies_pt[partonFlavor], eta).FillWeighted(chain.jet_pfCombinedMVAV2BJetTags[j] > btag_cut, weight, pt)

            # Vs. Pt and Vs. Eta (not updated for systematics!)
            #efficiencies_pt[flavor].FillWeighted(chain.jet_pfCombinedMVAV2BJetTags[j] > btag_cut, weight, pt)
            #efficiencies_eta[flavor].FillWeighted(chain.jet_pfCombinedMVAV2BJetTags[j] > btag_cut, weight, eta)

            #### 2D efficiencies
            if flavor == 5:
               object = btagging_eff_on_b[s]
            elif flavor == 4:
               object = btagging_eff_on_c[s]
            else:
               object = mistagging_eff_on_light[s]

            object.FillWeighted(chain.jet_pfCombinedMVAV2BJetTags[j] > btag_cut, weight, pt, eta)

    # Systematics
    for name, collections in systematics_jets.items():

        jets = collections['p4'](chain)

        njets = jets.size()

        for j in range(0, njets):
            pt = jets[j].Pt()
            eta = jets[j].Eta()

            if pt < 20:
                continue

            if eta > 2.4:
                continue

            flavor = ord(collections['flavor'](chain)[j])

            weight = systematics_on_nominal['nominal']['weight'](chain)
            object = None

            #### 1D efficiencies (not updated for systematics!)
            # if flavor == 5:
                # flavor = "b"
            # elif flavor == 4:
                # flavor = "c"
            # else:
                # flavor = "light"

            # # Vs. Pt in Eta bins
            # def find_bin(eff_dict, eta):
                # for bin, eff in eff_dict.items():
                    # if eta >= bin[0] and eta < bin[1]:
                        # return eff

            # find_bin(efficiencies_pt[flavor], eta).FillWeighted(chain.jet_pfCombinedMVAV2BJetTags[j] > btag_cut, weight, pt)

            # if partonFlavor == 21:
                # partonFlavor = "g"
            # elif partonFlavor == 1 or partonFlavor == 2 or partonFlavor == 3:
                # partonFlavor = "dus"
            # if isinstance(partonFlavor, str):
                # find_bin(efficiencies_pt[partonFlavor], eta).FillWeighted(chain.jet_pfCombinedMVAV2BJetTags[j] > btag_cut, weight, pt)

            # Vs. Pt and Vs. Eta (not updated for systematics!)
            #efficiencies_pt[flavor].FillWeighted(chain.jet_pfCombinedMVAV2BJetTags[j] > btag_cut, weight, pt)
            #efficiencies_eta[flavor].FillWeighted(chain.jet_pfCombinedMVAV2BJetTags[j] > btag_cut, weight, eta)

            #### 2D efficiencies
            if flavor == 5:
               object = btagging_eff_on_b[name]
            elif flavor == 4:
               object = btagging_eff_on_c[name]
            else:
               object = mistagging_eff_on_light[name]

            object.FillWeighted(collections['btag'](chain)[j] > btag_cut, weight, pt, eta)


print("Done")
output = ROOT.TFile.Open(output, "recreate")

## 1D efficiencies
# Vs. Pt in Eta bins
# for f in flavours:
    # for eff in efficiencies_pt[f].values():
        # eff.Write()
# Vs. Pt and Vs. Eta
#for f in flavours:
#    efficiencies_pt[f].Write()
#    efficiencies_eta[f].Write()

## 2D efficiencies
for s in btagging_eff_on_b.keys():
    btagging_eff_on_b[s].Write()
    btagging_eff_on_c[s].Write()
    mistagging_eff_on_light[s].Write()

output.Close()
