#! /usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.Reset()
from cp3_llbb.CommonTools.HistogramTools import getHistogramsFromFileRegex

#import os, sys, inspect
#scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#sys.path.append(scriptDir)
from subtractMCfromData import performSubtraction, addHistoDicos

import argparse

parser = argparse.ArgumentParser(description="Subtract MC from data for all histograms in a file.")
parser.add_argument("-d", "--data", nargs='+', help="Input files for data", required=True)
parser.add_argument("--dy", nargs='+', help="Input files for DY", required=True)
parser.add_argument("-m", "--mc", nargs='+', help="Input files for MC", required=True)
parser.add_argument("-o", "--output", help="Output file", required=True)
parser.add_argument("-s", "--syst", help="Take care of systematics", action="store_true")
options = parser.parse_args()

# FIXME
# Normalise backgrounds before subtraction
scale_ee = 0.937
scale_mumu = 0.967
# Normalise result of the subtraction
rescale_ee = 0.828
rescale_mumu = 0.879
LUMI = 35922

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

# Get SF histograms and perform the subtraction
print "Subtracting MuMu histograms"
histos_mumu = performSubtraction(options.data, options.mc, R".*MuMu.*_with_nobtag_to_btagM_reweighting$", LUMI, scale_mc=scale_mumu, rescale_result=rescale_mumu).values()
print "Subtracting ElEl histograms"
histos_ee = performSubtraction(options.data, options.mc, R".*ElEl.*_with_nobtag_to_btagM_reweighting$", LUMI, scale_mc=scale_ee, rescale_result=rescale_ee).values()

if options.syst:
    def build_syst(_list):
        _ret = []
        for _s in _list:
            _ret.append(_s + "up")
            _ret.append(_s + "down")
        return _ret
    def build_scale(_s):
        return [ _s + str(i) for i in range(6) ]

    # Systematics applied on both Data and MC
    systematics = ["jec", "jer", "jjbtaglight", "jjbtagheavy", "pu", "dyStat"]
    for _s in split_jec_sources:
        systematics.append("jec" + _s.lower())
    
    for _s in build_syst(systematics) + build_scale("dyScaleUncorr"):
        print "Handling systematics {}".format(_s)
        
        histos_mumu += performSubtraction(options.data, options.mc, R".*MuMu.*_with_nobtag_to_btagM_reweighting__" + _s + "$" , LUMI, scale_mc=scale_mumu, rescale_result=rescale_mumu).values()
        histos_ee += performSubtraction(options.data, options.mc, R".*ElEl.*_with_nobtag_to_btagM_reweighting__" + _s + "$" , LUMI, scale_mc=scale_ee, rescale_result=rescale_ee).values()

    # Systematics for which only MC is affected, not the reweighting => take nominal histos in Data
    systematics = ["elreco", "elidiso", "mutracking", "muid", "muiso", "trigeff", "pdf", "pdfqq", "pdfgg", "pdfqg", "hdamp"]
    
    for _s in build_syst(systematics) + build_scale("scaleUncorr"):
        print "Handling systematics {}".format(_s)
        
        histos_mumu += performSubtraction(options.data, options.mc, R".*MuMu.*_with_nobtag_to_btagM_reweighting$", LUMI, scale_mc=scale_mumu, rescale_result=rescale_mumu, mc_regexp=R".*MuMu.*_with_nobtag_to_btagM_reweighting__" + _s + "$", translation=(R"$", R"__" + _s)).values()
        histos_ee += performSubtraction(options.data, options.mc, R".*ElEl.*_with_nobtag_to_btagM_reweighting$", LUMI, scale_mc=scale_ee, rescale_result=rescale_ee, mc_regexp=R".*ElEl.*_with_nobtag_to_btagM_reweighting__" + _s + "$", translation=(R"$", R"__" + _s)).values()
        

# For MuE, get histograms from MC
print "Copying MuEl histograms"
histos_emu = getHistogramsFromFileRegex(options.dy[0], R".*MuEl.*btagM.*")
for file in options.dy[1:]:
    this_histos = getHistogramsFromFileRegex(file, R".*MuEl.*btagM.*")
    addHistoDicos(histos_emu, this_histos)

# Rename to have the same name as the other MC and data
for h in histos_ee + histos_mumu:
    old_name = h.GetName()
    new_name = old_name.replace("_with_nobtag_to_btagM_reweighting", "").replace("nobtag", "btagM")
    h.SetName(new_name)

print "Writing output"
# Write output
r_file = ROOT.TFile.Open(options.output, "recreate")
for hist in histos_mumu + histos_ee + histos_emu.values():
    hist.Write()
r_file.Close()

