#! /bin/env python

from __future__ import division

import math
from array import array

import ROOT
from DataFormats.FWLite import Events, Handle

ROOT.gROOT.SetBatch() 

datasets = {}
#datasets["SM"] = '/GluGluToHHTo2B2VTo2L2Nu_node_SM_13TeV-madgraph/RunIIFall15MiniAODv2-PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/MINIAODSIM'
#for i in range(2, 14):
#for i in range(4, 10):
for i in [2]:
    datasets[str(i)] = '/GluGluToHHTo2B2VTo2L2Nu_node_%d_13TeV-madgraph/RunIIFall15MiniAODv2-PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/MINIAODSIM' % i
#datasets["box"] = '/GluGluToHHTo2B2VTo2L2Nu_node_box_13TeV-madgraph/RunIIFall15MiniAODv2-PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/MINIAODSIM'

def get_dataset_files(dataset):
    import subprocess, json

    j = subprocess.check_output(['das_client', '--format', 'json', '--query', 'file dataset=%s' % dataset])

    data = json.loads(j)

    files = []

    for d in data["data"]:
        for f in d['file']:
            if 'dataset' in f:
                files.append(f['name'])
                print "Found file ", f['name']

    return [str('root://xrootd-cms.infn.it//%s') % str(f) for f in files]

def print_p4(p):
    return "%f %f %f %f" % (p.Px(), p.Py(), p.Pz(), p.E())

global_p1 = ROOT.Math.LorentzVector(ROOT.Math.PxPyPzE4D(ROOT.Double))(0, 0, 6500, 6500)
global_p2 = ROOT.Math.LorentzVector(ROOT.Math.PxPyPzE4D(ROOT.Double))(0, 0, -6500, 6500)

def get_cos_theta_star(h1, h2):

    hh = h1 + h2
    boost = ROOT.Math.Boost(-hh.X() / hh.T(), -hh.Y() / hh.T(), -hh.Z() / hh.T())

    p1 = boost(global_p1)
    p2 = boost(global_p2)

    newh1 = boost(h1)

    CSaxis =  ROOT.Math.DisplacementVector3D(ROOT.Math.Cartesian3D(ROOT.Double))(p1.Vect().Unit() - p2.Vect().Unit())

    return math.cos(ROOT.Math.VectorUtil.Angle(CSaxis.Unit(), newh1.Vect().Unit()))

handle = Handle("std::vector<reco::GenParticle>")
label = ("prunedGenParticles")

for node, dataset in datasets.items():

    print("Processing node %s" % node)

    print("Getting list of files from DAS...")
    files = get_dataset_files(dataset)
    print("Done.")

    output = ROOT.TFile.Open("gen_hh_node_%s.root" % node, "recreate")
    output_tree = ROOT.TTree("t", "t")
    higgses = []
    for i in range(2):
        higgses.append(ROOT.Math.PxPyPzEVector())
        output_tree.Branch("h_{}".format(i), higgses[i])

    hh = ROOT.Math.PxPyPzEVector()
    output_tree.Branch("hh", hh)

    cos_theta_star = array("f", [0])
    output_tree.Branch("cos_theta_star", cos_theta_star, "cos_theta_star/F")

    events = Events(files)
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

        if h1_index == -1 or h2_index == -1:
            print "Warning: could not find both Higgses!"
            continue

        higgses[0].__assign__(genParticles[h1_index].p4())
        higgses[1].__assign__(genParticles[h2_index].p4())

        hh.__assign__(higgses[0] + higgses[1])

        cos_theta_star[0] = get_cos_theta_star(higgses[0], higgses[1])

        output_tree.Fill()

    output.cd()
    output_tree.Write()
    output.Close()

    print("")
