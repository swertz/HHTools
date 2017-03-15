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


totalName = "DY_BDT_flat_SF_hh_llmetjj_HWWleptons_nobtag_cmva_no_cut"
passNameTemplate = "DY_BDT_flav_{}{}_SF_hh_llmetjj_HWWleptons_nobtag_cmva_no_cut"

parser = argparse.ArgumentParser(description='Compute different flavour fractions from histograms', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-i', '--input', nargs='+', help='Input ROOT files (plotter output AFTER hadd)', required=True)
parser.add_argument('-o', '--output', help='Output', required=True)
parser.add_argument('-t', '--total', default=totalName, help='Name of the histogram for all events (inclusive)')
parser.add_argument('-p', '--passed', default=passNameTemplate, help='Name of the "pass" histogram for the flavour fractions (with two "{}" being replaced by the flavours)')
parser.add_argument('-c', '--compare', help="If specified, create comparison plots of the efficiencies in the given folder")

options = parser.parse_args()

baseSystematics = ["pu", "pdf", "jec", "jer"]
#baseSystematics = ["elidiso", "muid", "muiso", "pu", "trigeff", "pdf", "jec", "jer"]
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
    assert(pas.GetNbinsX() == total.GetNbinsX())
    assert(pas.GetXaxis().GetXmax() == pas.GetXaxis().GetXmax()) 
    assert(pas.GetXaxis().GetXmin() == pas.GetXaxis().GetXmin()) 

    for i in range(0, total.GetNbinsX() + 2):
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
    totalHistos["total_" + getSystString(syst)] = []
    for flav1 in flavours:
        for flav2 in flavours:
            name = "{}{}_frac{}".format(flav1, flav2, getSystString(syst))
            passHistos[name] = []

for file in options.input:
    print "Reading histograms from file {}...".format(file)

    r_file = TFileWrapper.Open(file)
    if not r_file.IsOpen():
        raise Exception("Could not read from file {}".format(file))

    for syst in systematics:
        systString = getSystString(syst)
            
        totalHist = r_file.Get(options.total + systString)
        if not totalHist or not totalHist.InheritsFrom("TH1"):
            continue
        totalHist.SetDirectory(0)
        totalHistos["total_" + systString].append(totalHist)
        
        for flav1 in flavours:
            for flav2 in flavours:
                name = "{}{}_frac{}".format(flav1, flav2, systString)
                
                passHist = r_file.Get(options.passed.format(flav1, flav2) + systString)
                passHist.SetDirectory(0)

                passHistos[name].append(passHist)

    r_file.Close()

r_file = R.TFile.Open(options.output, "recreate")
if not r_file.IsOpen():
    raise Exception("Could not read from file {}".format(options.output))

flavourFractions = {}

for syst in systematics:
    systString = getSystString(syst)
    
    addHistos(totalHistos["total_" + systString])
    
    for flav1 in flavours:
        for flav2 in flavours:
            name = "{}{}_frac{}".format(flav1, flav2, systString)
            addHistos(passHistos[name])
            print "Doing " + name
            passHisto = passHistos[name][0]
            totalHisto = totalHistos["total_" + systString][0]
            checkHistos(passHisto, totalHisto)
            thisEff = R.TEfficiency(passHisto, totalHisto)
            thisEff.SetName(name)
            thisEff.SetStatisticOption(R.TEfficiency.kBUniform)
            flavourFractions[name] = thisEff
            thisEff.Write()

r_file.Close()

if options.compare is not None:
    outDir = options.compare
    if not os.path.isdir(outDir):
        os.mkdir(outDir)

    for flav1 in flavours:
        for flav2 in flavours:
            name = "{}{}_frac".format(flav1, flav2)
            
            for syst in baseSystematics:    
                graphs = {}
                if "scaleUncorr" in syst or "dyScale" in syst:
                    graphs["nominal"] = flavourFractions[name].CreateGraph()
                    for i in range(6):
                        graphs[str(i)] = flavourFractions[name + "__" + syst + str(i)].CreateGraph()
                else:
                    graphs = {
                            "nominal": flavourFractions[name].CreateGraph(),
                            "up": flavourFractions[name + "__" + syst + "up"].CreateGraph(),
                            "down": flavourFractions[name + "__" + syst + "down"].CreateGraph()
                        }
                
                leg = R.TLegend(0.7, 0.91, 0.943, 1.)
                leg.SetNColumns(3)
                for item in graphs.items():
                    leg.AddEntry(item[1], item[0], "P")

                drawTGraph(graphs.values(), "{}{}_{}".format(flav1, flav2, syst), legend=leg, xLabel="DY BDT", yLabel="Flavour fraction for {}{}".format(flav1, flav2), leftText="Systematic: " + syst, dir=outDir)
                
            drawTGraph([flavourFractions[name].CreateGraph()], "{}{}_nominal".format(flav1, flav2), legend=None, xLabel="DY BDT", yLabel="Fraction", leftText="Nominal flavour fraction for {}{}".format(flav1, flav2), dir=outDir)
