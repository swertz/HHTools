#! /bin/env python

import argparse
import os
import sys

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

h_njets_b = ROOT.TH2F("njets_b", "njets_b", 100, 20, 300, 100, -3, 3)
h_njets_b_btagged = ROOT.TH2F("njets_b_btagged", "njets_b_btagged", 100, 20, 300, 100, -3, 3)

h_njets_c = ROOT.TH2F("njets_c", "njets_c", 100, 20, 300, 100, -3, 3)
h_njets_c_btagged = ROOT.TH2F("njets_c_btagged", "njets_c_btagged", 100, 20, 300, 100, -3, 3)

h_njets_light = ROOT.TH2F("njets_light", "njets_light", 100, 20, 300, 100, -3, 3)
h_njets_light_mistagged = ROOT.TH2F("njets_light_mistagged", "njets_light_mistagged", 100, 20, 300, 100, -3, 3)

btag_cut = 0.800

chain = ROOT.TChain('t')
for f in files:
    chain.Add(f)

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
        eta = chain.jet_p4[j].Eta()

        if pt < 20:
            continue
        
        flavor = ord(chain.jet_hadronFlavor[j])

        if flavor == 5:
            h_njets_b.Fill(pt, eta)
            if chain.jet_pfCombinedInclusiveSecondaryVertexV2BJetTags[j] > btag_cut:
                h_njets_b_btagged.Fill(pt, eta)
        elif flavor == 4:
            h_njets_c.Fill(pt, eta)
            if chain.jet_pfCombinedInclusiveSecondaryVertexV2BJetTags[j] > btag_cut:
                h_njets_c_btagged.Fill(pt, eta)
        else:
            h_njets_light.Fill(pt, eta)
            if chain.jet_pfCombinedInclusiveSecondaryVertexV2BJetTags[j] > btag_cut:
                h_njets_light_mistagged.Fill(pt, eta)


print("Done")
output = ROOT.TFile.Open(output, "recreate")

h_njets_b.Write()
h_njets_b_btagged.Write()

h_njets_c.Write()
h_njets_c_btagged.Write()

h_njets_light.Write()
h_njets_light_mistagged.Write()

if not options.json:
    btagging_eff_on_b = h_njets_b_btagged.Clone("btagging_eff_on_b")
    btagging_eff_on_b.Divide(h_njets_b)

    btagging_eff_on_c = h_njets_c_btagged.Clone("btagging_eff_on_c")
    btagging_eff_on_c.Divide(h_njets_c)

    mistagging_eff_on_light = h_njets_light_mistagged.Clone("mistagging_eff_on_light")
    mistagging_eff_on_light.Divide(h_njets_light)

    btagging_eff_on_b.Write()
    btagging_eff_on_c.Write()
    mistagging_eff_on_light.Write()

output.Close()
