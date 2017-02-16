#!/usr/bin/env python

import ROOT
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputs", nargs='+')
parser.add_argument("--lljj", action="store_true")
parser.add_argument("-s", "--stage", type=str, default="no_cut")
parser.add_argument("-c", "--cat", type=str, required=True, choices=["MuMu", "MuEl", "ElEl", "SF", "All"])
parser.add_argument("-l", "--lumi", type=float, default=36809.)
args = parser.parse_args()

base_syst = ["jec", "jer", "pu", "elidiso", "muid", "muiso", "trigeff", "pdf", "scaleUncorr", "jjbtagheavy", "jjbtaglight", "dyStat", "dyScaleUncorr"]
if args.lljj:
    base_syst = ["jec", "jer", "pu", "elidiso", "muid", "muiso", "trigeff", "pdf", "scaleUncorr"]
base_syst += ["pdfgg", "pdfqq", "pdfqg"]
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
    base_syst.append("jec" + _s.lower())

name = "cosThetaStar_{}_hh_llmetjj_HWWleptons_btagM_cmva_{}".format(args.cat, args.stage)
if args.lljj:
    name = "cosThetaStar_{}_hh_llmetjj_HWWleptons_nobtag_cmva_{}".format(args.cat, args.stage)

nominal = 0
syst_yields= {}
for syst in base_syst:
    syst_yields[syst] = [0,0]

def get_integral_checked(file_handle, name):
    _h = file_handle.Get(name)
    if not _h.InheritsFrom("TH1"):
        return 0
    return _h.Integral() * args.lumi

for input in args.inputs:
    _f = ROOT.TFile.Open(input)

    nominal += get_integral_checked(_f, name)

    for _s in base_syst:
        up = get_integral_checked(_f, name + "__" + _s + "up")
        down = get_integral_checked(_f, name + "__" + _s + "down")
        syst_yields[_s][0] += up
        syst_yields[_s][1] += down

    _f.Close()

print "Nominal yield: {}".format(nominal)
for _s in base_syst:
    print("{}: +{}% / -{}%".format(_s, 100*abs(syst_yields[_s][0]-nominal)/nominal, 100*abs(syst_yields[_s][1]-nominal)/nominal))
