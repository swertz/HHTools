#! /bin/env python

from __future__ import division

import argparse
import ROOT as R
R.PyConfig.IgnoreCommandLineOptions = True
R.gROOT.Reset()

totalName = "DY_BDT_flat_All_hh_llmetjj_HWWleptons_nobtag_cmva_no_cut"
passNameTemplate = "DY_BDT_flav_{}{}_All_hh_llmetjj_HWWleptons_nobtag_cmva_no_cut"

parser = argparse.ArgumentParser(description='Compute different flavour fractions from histograms', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-i', '--input', nargs='+', help='Input ROOT files (plotter output AFTER hadd)', required=True)
parser.add_argument('-o', '--output', help='Output', required=True)
parser.add_argument('-s', '--scale', action='store_true', help='Scale by process XS/sum(weights). Is most likely already done if it comes from the plotter')
parser.add_argument('-t', '--total', default=totalName, help='Name of the histogram for all events (inclusive)')
parser.add_argument('-p', '--passed', default=passNameTemplate, help='Name of the "pass" histogram for the flavour fractions (with two "{}" being replaced by the flavours)')

options = parser.parse_args()

systematics = ["nominal", "elidisoup", "elidisodown", "muidup", "muiddown", "muisoup", "muisodown", "puup", "pudown", "trigeffup", "trigeffdown", "pdfup", "pdfdown", "scaleUncorrup", "scaleUncorrdown"]

flavours = ["b", "c", "l"]

def getSystString(syst):
    if syst == "nominal":
        return ""
    else:
        return "__" + syst

flavourFractions = {}
for flav1 in flavours:
    for flav2 in flavours:
        for syst in systematics:
            name = "{}{}_frac{}".format(flav1, flav2, getSystString(syst))
            flavourFractions[name] = []

for file in options.input:
    print "Building TEfficiency objects from file {}...".format(file)

    r_file = R.TFile.Open(file)
    if not r_file.IsOpen():
        raise Exception("Could not read from file {}".format(file))

    for syst in systematics:
        systString = getSystString(syst)
        
        for flav1 in flavours:
            for flav2 in flavours:
                name = "{}{}_frac{}".format(flav1, flav2, systString)
                
                totalHist = r_file.Get(totalName + systString)
                passHist = r_file.Get(passNameTemplate.format(flav1, flav2) + systString)
                
                thisEff = R.TEfficiency(passHist, totalHist)
                thisEff.SetName(name)
                thisEff.SetStatisticOption(R.TEfficiency.kBJeffrey)
                
                if options.scale:
                    try:
                        xs = r_file.Get("cross_section").GetVal()
                    except:
                        print "Did not find cross section, will use 1."
                        xs = 1
                    try:
                        wgt_sum = r_file.Get("event_weight_sum").GetVal()
                        print "Did not find event weight sum, will use 1."
                    except:
                        wgt_sum = 1
                    
                    thisEff.SetWeight(xs / wgt_sum)

                flavourFractions[name].append(thisEff)

    r_file.Close()

r_file = R.TFile.Open(options.output, "recreate")
if not r_file.IsOpen():
    raise Exception("Could not read from file {}".format(options.output))

for fracList in flavourFractions.values():
    thisFrac = fracList[0]
    for frac in fracList[1:]:
        thisFrac.Add(frac)
    thisFrac.Write()

r_file.Close()
