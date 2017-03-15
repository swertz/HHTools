#!/usr/bin/env python

import re

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.Reset()
from cp3_llbb.CommonTools.HistogramTools import getHistogramsFromFileRegex

def addHistoDicos(dic1, dic2, alpha=1):
    if sorted(dic1.keys()) != sorted(dic2.keys()):
        raise Exception("Error: name mismatch between histograms")
    for key in dic1.keys():
        dic1[key].Add(dic2[key], alpha)

def performSubtraction(data, mc, regexp, lumi, verbose=False, mc_regexp=None, translation=None, scale_mc=1., rescale_result=1.):
    if mc_regexp is not None and regexp != mc_regexp and translation is None:
        raise Exception("Invalid input")

    # First get a list of histograms using the first data file
    if verbose: print "Reading histograms from {}...".format(data[0])
    histograms = getHistogramsFromFileRegex(data[0], regexp)

    if verbose:
        print "{} histograms considered:".format(len(histograms.keys()))
        for hist in sorted(histograms.keys()):
            print hist

    # For each data (MC) file and each histogram, add (subtract) from the previous ones
    for d in data[1:]:
        if verbose: print "Reading histograms from {}...".format(d)
        this_histos = getHistogramsFromFileRegex(d, regexp)
        if verbose: print "Found {} histograms.".format(len(this_histos.keys()))
        addHistoDicos(histograms, this_histos)

    # If we consider a luminosity, we have to divide the data by the lumi, since the MC is NOT scaled by it!
    # PlotIt will then rescale the DY contribution correctly
    if lumi:
        for hist in histograms.values():
            hist.Scale(1. / lumi)
        
    # MC: slightly more difficult treatment, account for replacements
    if mc_regexp is None:
        mc_regexp = regexp
    
    if verbose: print "Reading histograms from {}...".format(mc[0])
    mc_histograms = getHistogramsFromFileRegex(mc[0], mc_regexp)
    if verbose: print "Found {} histograms.".format(len(mc_histograms.keys()))
    
    for mc in mc[1:]:
        if verbose: print "Reading histograms from {}...".format(mc)
        this_histos = getHistogramsFromFileRegex(mc, mc_regexp)
        if verbose: print "Found {} histograms.".format(len(this_histos.keys()))
        addHistoDicos(mc_histograms, this_histos)

    # No replacement to do: easy
    if regexp == mc_regexp:
        if verbose: print("Performing subtraction on histograms!")
        addHistoDicos(histograms, mc_histograms, -scale_mc)
        if rescale_result != 1:
            for _h in histograms.values():
                _h.Scale(rescale_result)
        
        return histograms

    # Replacements to do
    # First rename the MC histograms with the replacement
    if verbose: print("Performing replacement on histogram names!")
    new_histograms = {}
    for h in histograms.items():
        new_name = re.sub(translation[0], translation[1], h[1].GetName())
        h[1].SetName(new_name)
        new_histograms[new_name] = h[1]

    if verbose: print("Performing subtraction on histograms!")
    addHistoDicos(new_histograms, mc_histograms, -scale_mc)
    
    if rescale_result != 1:
        for _h in new_histograms.values():
            _h.Scale(rescale_result)

    return new_histograms



if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Subtract MC from data for all histograms in a file.")
    parser.add_argument("-d", "--data", nargs='+', help="Input files for data", required=True)
    parser.add_argument("-m", "--mc", nargs='+', help="Input files for MC", required=True)
    parser.add_argument("-o", "--output", help="Output file", required=True)
    parser.add_argument("-r", "--regexp", help="Regexp that must be matched by the histogram names to be considered", default=R".*_with_nobtag_to_btagM_reweighting$")
    parser.add_argument("-l", "--lumi", type=float, help="Scale Data by luminosity", default=36810)
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose")
    options = parser.parse_args()

    histos = performSubtraction(options.data, options.mc, options.regexp, options.lumi, options.verbose)

    # Write output
    r_file = ROOT.TFile.Open(options.output, "recreate")
    for hist in histos.values():
        hist.Write()
    r_file.Close()
