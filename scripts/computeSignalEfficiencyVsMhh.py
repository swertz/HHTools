#! /bin/env python

import argparse
import ROOT as R

parser = argparse.ArgumentParser(description="Compute signal selection efficiency as a function of gen-level m(hh),\
using a TTree containing m(hh) for all generated events retrieved using 'getHHGenVectors.py', \
and a TH1 created e.g. using histFactory containing m(hh) after full selection.\
The binning and range of the efficiency will be taken from the latter histogram.")

parser.add_argument('-o', '--output', help='Output file', required=True)
parser.add_argument('-i', '--input', help='Input file containing the gen-level m(hh) histogram after selection', required=True)
parser.add_argument('-t', '--hist', help='Name of the histogram in the input file', default='gen_mHH')
parser.add_argument('-g', '--gen', help='Input file containing a ttree with hh in it', required=True)

args = parser.parse_args()

## Retrieve histogram with m(hh), cross section, event weight sum
in_file = R.TFile.Open(args.input)
if not in_file.IsOpen():
    raise Exception("Could not open file {}".format(args.input))

selected_hist = in_file.Get(args.hist)
if not selected_hist.InheritsFrom("TH1"):
    raise Exception("Could not retrieve histogram {}".format(args.hist))
selected_hist.SetName("selected_mhh")

xs = in_file.Get("cross_section").GetVal()
evt_wgt_sum = in_file.Get("event_weight_sum").GetVal()

selected_hist.SetDirectory(0)
in_file.Close()

## Build histogram with gen-level m(hh), same binning
in_file = R.TFile.Open(args.gen)
if not in_file.IsOpen():
    raise Exception("Could not open file {}".format(args.gen))

gen_hist = selected_hist.Clone("gen_level_mhh")
gen_hist.Reset()

tree = in_file.Get("t")
tree.Draw("hh.M()>>gen_level_mhh", "", "")
gen_hist.SetDirectory(0)

#gen_hist.Scale(0.001 / tree.GetEntries()) # In case the TParameters are not present... signals are 1fb
gen_hist.Scale(xs / evt_wgt_sum)

in_file.Close()

## Do the efficiency, store everything
out_file = R.TFile(args.output, "recreate")
if not out_file.IsOpen() or out_file.IsZombie():
    raise Exception("Could not open file {}".format(args.output))

eff = R.TEfficiency(selected_hist, gen_hist)
eff.SetStatisticOption(R.TEfficiency.kMidP)

eff.SetName("efficiency")

eff.Write()
selected_hist.Write()
gen_hist.Write()

out_file.Close()
