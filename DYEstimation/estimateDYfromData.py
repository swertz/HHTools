#! /usr/bin/env python

import argparse

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.Reset()
from cp3_llbb.CommonTools.HistogramTools import getHistogramsFromFileRegex

parser = argparse.ArgumentParser(description="Subtract MC from data for all histograms in a file.")
parser.add_argument("-d", "--data", nargs='+', help="Input files for data", required=True)
parser.add_argument("-m", "--mc", nargs='+', help="Input files for MC", required=True)
parser.add_argument("-o", "--output", help="Output file", required=True)
parser.add_argument("-r", "--regexp", help="Regexp that must be matched by the histogram names to be considered", default=R".*_with_nobtag_to_btagM_reweighting$")
parser.add_argument("-l", "--lumi", type=float, help="Scale MC by luminosity", default=36151.504)
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose")
options = parser.parse_args()

def addHistoDicos(dic1, dic2, alpha):
    for item in dic1.items():
        item[1].Add(dic2[item[0]], alpha)

# First get a list of histograms using the first data file
if options.verbose: print "Reading histograms from {}...".format(options.data[0])
histograms = getHistogramsFromFileRegex(options.data[0], options.regexp)

if options.verbose:
    print "{} histograms considered:".format(len(histograms.keys()))
    for hist in sorted(histograms.keys()):
        print hist

# For each data (MC) file and each histogram, add (subtract) from the previous ones
for d in options.data[1:]:
    if options.verbose: print "Reading histograms from {}...".format(d)
    
    this_histos = getHistogramsFromFileRegex(d, options.regexp)
    
    if options.verbose: print "Found {} histograms.".format(len(this_histos.keys()))
    
    addHistoDicos(histograms, this_histos, 1)

# If we consider a luminosity, we have to divide the data by the lumi, since the MC is NOT scaled by it!
# PlotIt will then rescale the DY contribution correctly
if options.lumi:
    for hist in histograms.values():
        hist.Scale(1. / options.lumi)
    
for mc in options.mc:
    if options.verbose: print "Reading histograms from {}...".format(mc)
    
    this_histos = getHistogramsFromFileRegex(mc, options.regexp)
    
    if options.verbose: print "Found {} histograms.".format(len(this_histos.keys()))
    
    addHistoDicos(histograms, this_histos, -1)

# Write output
r_file = ROOT.TFile.Open(options.output, "recreate")
for hist in histograms.values():
    hist.Write()
r_file.Close()
