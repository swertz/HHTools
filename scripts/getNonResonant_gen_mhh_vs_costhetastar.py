#! /bin/env python

from __future__ import division

import math

import ROOT
from DataFormats.FWLite import Events, Handle

ROOT.gROOT.SetBatch() 

datasets = []
for i in range(2, 14):
    datasets.append('/GluGluToHHTo2B2VTo2L2Nu_node_%d_13TeV-madgraph/RunIIFall15MiniAODv2-PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/MINIAODSIM' % i)

def get_dataset_files(dataset):
    import subprocess, json

    j = subprocess.check_output(['das_client', '--format', 'json', '--query', 'file dataset=%s' % dataset])

    data = json.loads(j)

    files = []

    for d in data["data"]:
        for f in d['file']:
            if 'dataset' in f:
                files.append(f['name'])

    return [str('root://xrootd-cms.infn.it//%s') % str(f) for f in files]

def print_p4(p):
    return "%f %f %f %f" % (p.Px(), p.Py(), p.Pz(), p.E())

global_p1 = ROOT.Math.LorentzVector(ROOT.Math.PxPyPzE4D(ROOT.Double))(0, 0, 6500, 6500)
global_p2 = ROOT.Math.LorentzVector(ROOT.Math.PxPyPzE4D(ROOT.Double))(0, 0, -6500, 6500)
def cos_theta_star(h1, h2):

    hh = h1 + h2
    boost = ROOT.Math.Boost(-hh.X() / hh.T(), -hh.Y() / hh.T(), -hh.Z() / hh.T())

    p1 = boost(global_p1)
    p2 = boost(global_p2)

    newh1 = boost(h1)

    CSaxis =  ROOT.Math.DisplacementVector3D(ROOT.Math.Cartesian3D(ROOT.Double))(p1.Vect().Unit() - p2.Vect().Unit())

    return math.cos(ROOT.Math.VectorUtil.Angle(CSaxis.Unit(), newh1.Vect().Unit()))


handle = Handle("std::vector<reco::GenParticle>")
label = ("prunedGenParticles")

sum_map = ROOT.TH2F("mhh_vs_cos_theta_star", "mhh_vs_cos_theta_star", 90, 0, 1800, 10, -1, 1)
sum_map_abs = ROOT.TH2F("mhh_vs_abs_cos_theta_star", "mhh_vs_abs_cos_theta_star", 90, 0, 1800, 5, 0, 1)

for dataset in datasets:

    name = dataset[1:dataset.index('_13TeV')]
    print("Processing %s" % name)

    print("Getting list of files from DAS...")
    files = get_dataset_files(dataset)
    print("Done.")

    output = ROOT.TFile.Open("%s_mhh_vs_cos_theta_star.root" % name, "recreate")
    output.cd()
    map = ROOT.TH2F("mhh_vs_cos_theta_star", "mhh_vs_cos_theta_star", 90, 0, 1800, 10, -1, 1)
    map_abs = ROOT.TH2F("mhh_vs_abs_cos_theta_star", "mhh_vs_abs_cos_theta_star", 90, 0, 1800, 5, 0, 1)

    events = Events(files)
    #events = Events('1E311A6B-C2C7-E511-BCA6-141877411C7F.root', maxEvents=100)
    n_events = events.size()

    for i, event in enumerate(events):

        if ((i % 5000) == 0):
            print("Processing event %d over %d (%f%% done)" % (i + 1, n_events, i / n_events * 100))

        event.getByLabel(label, handle)

        genParticles = handle.product()

        h1_index = -1
        h2_index = -1
        
        # Select the two higgs
        for index, p in enumerate(genParticles):
            if p.pdgId() == 25 and p.isHardProcess():
                if h1_index == -1:
                    h1_index = index
                elif h2_index == -1:
                    h2_index = index
                    break

        h1_p4 = genParticles[h1_index].p4()
        h2_p4 = genParticles[h2_index].p4()

        p = h1_p4 + h2_p4
        c = cos_theta_star(h1_p4, h2_p4)
        map.Fill(p.M(), c)
        sum_map.Fill(p.M(), c)

        map_abs.Fill(p.M(), math.fabs(c))
        sum_map_abs.Fill(p.M(), math.fabs(c))

    output.cd()
    map.Write()
    map_abs.Write()
    output.Close()

    print("")

output = ROOT.TFile.Open("GluGluToHHTo2B2VTo2L2Nu_all_nodes_gen_mhh_vs_costhetastar.root", "recreate")
sum_map.Write()
sum_map_abs.Write()
output.Close()
