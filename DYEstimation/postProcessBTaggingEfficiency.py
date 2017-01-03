#! /bin/env python

import argparse
import os
import sys

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.Reset()

parser = argparse.ArgumentParser(description='Compute b-tagging efficiency on a given sample')

parser.add_argument('input', type=str, metavar='FILE', help='Input ROOT file containing btagging efficiency histograms')

options = parser.parse_args()

ROOT.TH1.SetDefaultSumw2(True)

f = ROOT.TFile.Open(options.input, "update")

h_njets_b = f.Get("njets_b")
h_njets_b_btagged = f.Get("njets_b_btagged")

h_njets_c = f.Get("njets_c")
h_njets_c_btagged = f.Get("njets_c_btagged")

h_njets_light = f.Get("njets_light")
h_njets_light_mistagged = f.Get("njets_light_mistagged")

btagging_eff_on_b = h_njets_b_btagged.Clone("btagging_eff_on_b")
btagging_eff_on_b.Divide(h_njets_b)

btagging_eff_on_c = h_njets_c_btagged.Clone("btagging_eff_on_c")
btagging_eff_on_c.Divide(h_njets_c)

mistagging_eff_on_light = h_njets_light_mistagged.Clone("mistagging_eff_on_light")
mistagging_eff_on_light.Divide(h_njets_light)

btagging_eff_on_b.Write()
btagging_eff_on_c.Write()
mistagging_eff_on_light.Write()

f.Close()

print("Input file updated with new histograms")
