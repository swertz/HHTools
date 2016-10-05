#!/usr/bin/env python

import ROOT as R
from os.path import join

baseDir = "/home/fynu/sbrochet/scratch/Framework/CMSSW_7_6_5/src/cp3_llbb/HHTools/histFactory_hh"
condorDir = "160706_all_newjer_newtraining_fixedcluster7_0"

outDir = join(baseDir, condorDir, "condor", "output")

signalBaseStr = "GluGluToHHTo2B2VTo2L2Nu_node_{node}_13TeV-madgraph_v0.1.4+76X_HHAnalysis_2016-06-03.v0_histos.root"

nodes = ["SM", "box"] + range(1, 13)
limits = {
        2: 1,
        5: 2,
        9: 3,
        1: 4,
        8: 5,
        3: 6,
        6: 7,
        11: 8,
        4: 9,
        "SM": 10,
        "box": 11,
        10: 12,
        12: 13,
        7: 14,
    }

histName = "llmetjj_M_All_hh_llmetjj_HWWleptons_btagM_csv_mll_cut"

lumi = 2300
xs = 10000

cut = 800
actualCut = 0

integrals = []

for n in nodes:
    fileName = join(outDir, signalBaseStr.format(node=n))
    file = R.TFile(fileName)
    histo = file.Get(histName)

    firstBin = histo.FindBin(cut)
    actualCut = histo.GetBinLowEdge(firstBin)
    lastBin = histo.GetNbinsX() + 1
    integral = histo.Integral(firstBin, lastBin)

    integrals.append( (n, integral) )

integrals.sort(key=lambda x: x[1], reverse=True)

print "Integral of {} > {} (for XS={}fb, intL={}/pb)".format(histName, actualCut, xs, lumi)
for i in integrals:
    print "Node {:>3}: {: >6.1f} -- {:2}".format(i[0], i[1]*lumi*xs, limits[i[0]])
