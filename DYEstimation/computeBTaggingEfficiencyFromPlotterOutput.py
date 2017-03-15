#! /bin/env python

from __future__ import division

import argparse
import ROOT as R
R.PyConfig.IgnoreCommandLineOptions = True
R.gROOT.Reset()
R.gROOT.SetBatch(1)

import os
import sys

CMSSW_BASE = os.environ['CMSSW_BASE']
SCRAM_ARCH = os.environ['SCRAM_ARCH']
sys.path.append(os.path.join(CMSSW_BASE, 'src', 'cp3_llbb', 'CommonTools', 'toolBox'))

from drawCanvas import drawTGraph
from cp3_llbb.CommonTools import TFileWrapper


totalNameTemplate = "btag_efficiency_jet_{}_all_flav_{}_All_hh_llmetjj_HWWleptons_nobtag_cmva_no_cut"
passNameTemplate = "btag_efficiency_jet_{}_tagged_flav_{}_All_hh_llmetjj_HWWleptons_nobtag_cmva_no_cut"

parser = argparse.ArgumentParser(description='Compute different flavour fractions from histograms', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-i', '--input', nargs='+', help='Input ROOT files (plotter output AFTER hadd)', required=True)
parser.add_argument('-o', '--output', help='Output', required=True)
parser.add_argument('-t', '--total', default=totalNameTemplate, help='Name of the histograms for untagged jets (with two "{}" being replaced by the jet number and the jet flavour')
parser.add_argument('-p', '--passed', default=passNameTemplate, help='Name of the histograms for tagged jets (with two "{}" being replaced by the jet number and the jet flavour)')
parser.add_argument('-n', '--njets', default=5, help='Max. number of jets')

options = parser.parse_args()


#baseSystematics = ["elidiso", "muid", "muiso", "pu", "trigeff", "pdf", "jec", "jer"]
baseSystematics = ["pu", "pdf", "jec", "jer"]
for _s in ["qq", "gg", "qg"]:
    baseSystematics.append("pdf" + _s)
split_jec_sources = [
                "AbsoluteFlavMap",
                "AbsoluteMPFBias",
                "AbsoluteScale",
                "AbsoluteStat",
                "FlavorQCD",
                "Fragmentation",
                "PileUpDataMC",
                "PileUpPtBB",
                "PileUpPtEC1",
                "PileUpPtEC2",
                "PileUpPtHF",
                "PileUpPtRef",
                "RelativeBal",
                "RelativeFSR",
                "RelativeJEREC1",
                "RelativeJEREC2",
                "RelativeJERHF",
                "RelativePtBB",
                "RelativePtEC1",
                "RelativePtEC2",
                "RelativePtHF",
                "RelativeStatEC",
                "RelativeStatFSR",
                "RelativeStatHF",
                "SinglePionECAL",
                "SinglePionHCAL",
                "TimePtEta"]
for _s in split_jec_sources:
    baseSystematics.append("jec" + _s.lower())

systematics = ["nominal"]
for syst in baseSystematics:
    systematics.append(syst + "up")
    systematics.append(syst + "down")

baseSystematics.append("scaleUncorr")
for i in range(6):
    systematics.append("scaleUncorr{}".format(i))


flavours = ["b", "c", "l"]

def getSystString(syst):
    if syst == "nominal":
        return ""
    else:
        return "__" + syst

def addHistos(lst):
    if len(lst) == 0:
        return
    for h in lst[1:]:
        lst[0].Add(h)

def checkHistos(pas, total):
    assert(pas.GetNcells() == total.GetNcells())
    assert(pas.GetXaxis().GetXmax() == pas.GetXaxis().GetXmax()) 
    assert(pas.GetXaxis().GetXmin() == pas.GetXaxis().GetXmin()) 
    assert(pas.GetYaxis().GetXmax() == pas.GetYaxis().GetXmax()) 
    assert(pas.GetYaxis().GetXmin() == pas.GetYaxis().GetXmin()) 

    for i in range(0, total.GetNcells()):
        if total.GetBinContent(i) < pas.GetBinContent(i):
            print "Warning: histogram {} inconsistent bin content for bin {}: {} > {}".format(total.GetName(), i, pas.GetBinContent(i), total.GetBinContent(i))
            pas.SetBinContent(i, total.GetBinContent(i))
        if total.GetBinContent(i) < 0:
            print "Warning: histogram {} inconsistent bin content for bin {}: {}".format(total.GetName(), i, total.GetBinContent(i))
            total.SetBinContent(i, 0)
        if pas.GetBinContent(i) < 0:
            print "Warning: histogram {} inconsistent bin content for bin {}: {}".format(pas.GetName(), i, pas.GetBinContent(i))
            pas.SetBinContent(i, 0)

passHistos = {}
totalHistos = {}
for syst in systematics:
    for flav in flavours:
        name = flav + getSystString(syst)
        passHistos[name] = []
        totalHistos[name] = []

for file in options.input:
    print "Reading histograms from file {}...".format(file)

    r_file = TFileWrapper.Open(file)
    if not r_file.IsOpen():
        raise Exception("Could not read from file {}".format(file))

    for syst in systematics:
        for flav in flavours:
            name = flav + getSystString(syst)
            for ijet in range(options.njets):
                totalHist = r_file.Get(options.total.format(ijet, flav) + getSystString(syst))
                if not totalHist or not totalHist.InheritsFrom("TH2"):
                    continue
                totalHist.SetDirectory(0)
                totalHistos[name].append(totalHist)
            
                passHist = r_file.Get(options.passed.format(ijet, flav) + getSystString(syst))
                passHist.SetDirectory(0)
                passHistos[name].append(passHist)

    r_file.Close()

r_file = R.TFile.Open(options.output, "recreate")
if not r_file.IsOpen():
    raise Exception("Could not read from file {}".format(options.output))

for syst in systematics:
    for flav in flavours:
        name = flav + getSystString(syst)

        addHistos(totalHistos[name])
        addHistos(passHistos[name])
        
        print "Doing " + name
        passHisto = passHistos[name][0]
        totalHisto = totalHistos[name][0]
        checkHistos(passHisto, totalHisto)
        thisEff = R.TEfficiency(passHisto, totalHisto)
        thisEff.SetName("btagging_eff_on_" + name)
        thisEff.SetStatisticOption(R.TEfficiency.kBUniform)
        thisEff.Write()

r_file.Close()
