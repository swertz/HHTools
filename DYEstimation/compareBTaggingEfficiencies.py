#! /bin/env python

import ROOT as R
R.gROOT.SetBatch(1)

import os
import sys

CMSSW_BASE = os.environ['CMSSW_BASE']
SCRAM_ARCH = os.environ['SCRAM_ARCH']
sys.path.append(os.path.join(CMSSW_BASE, 'src', 'cp3_llbb', 'CommonTools', 'toolBox'))

from drawCanvas import drawTGraph

outDir = "bTaggingComparisonPlots_EtaBins"

if not os.path.isdir(outDir):
    os.mkdir(outDir)

def get_obj(file, key):
    tfile = R.TFile.Open(file)
    obj = tfile.Get(key)
    obj.SetDirectory(0)
    tfile.Close()
    return obj

## Compare DY and TTbar
files = {
        "DY": "161222_btaggingEfficiencyOnCondor_DY/condor/output/btagging_efficiency.root",
        "TTbar": "161222_btaggingEfficiencyOnCondor_TT/condor/output/btagging_efficiency.root"
        }

for flav in ["b", "c", "light"]:
    
    #for var in ["pt", "eta"]:
    eta_binning = [0, 0.6, 1.2, 1.8, 2.4]
    for bin in range(len(eta_binning) - 1):
        eta_range = (eta_binning[bin], eta_binning[bin+1])
        
        effName = "btagging_eff_on_" + flav + "_vs_pt_eta_" + str(eta_range)
        #effName = "btagging_eff_on_" + flav + "_vs_" + var
        graphs = { f[0]: get_obj(f[1], effName).CreateGraph() for f in files.items() }

        leg = R.TLegend(0.7, 0.91, 0.943, 1.)
        leg.SetNColumns(2)
        for item in graphs.items():
            leg.AddEntry(item[1], item[0], "P")

        text = str(eta_range[0]) + " <= |#eta| < " + str(eta_range[1])
        drawTGraph(graphs.values(), effName, xLabel="pt", yLabel="B-tagging eff. for {}-jets".format(flav), legend=leg, leftText=text, formats=["pdf", "png"], dir=outDir, ratio=(0,1))

## Compare g and uds
#file = "161223_btaggingEfficiencyOnCondor_TT_checkLight/condor/output/btagging_efficiency.root"
#flavours = ["g", "dus"]
#eta_binning = [0, 0.6, 1.2, 1.8, 2.4]
#
#for bin in range(len(eta_binning) - 1):
#    eta_range = (eta_binning[bin], eta_binning[bin+1])
#    
#    effName = "btagging_eff_on_{}_vs_pt_eta_" + str(eta_range)
#    graphs = { "{}-jets".format(f): get_obj(file, effName.format(f)).CreateGraph() for f in flavours }
#
#    leg = R.TLegend(0.7, 0.91, 0.943, 1.)
#    leg.SetNColumns(2)
#    for item in graphs.items():
#        leg.AddEntry(item[1], item[0], "P")
#
#    text = str(eta_range[0]) + " <= |#eta| < " + str(eta_range[1])
#    drawTGraph(graphs.values(), "btagging_eff_vs_pt_eta" + str(eta_range), legend=leg, xLabel="pt", yLabel="B-tagging eff.", leftText=text, formats=["pdf", "png"], dir=outDir, ratio=(0,1))
