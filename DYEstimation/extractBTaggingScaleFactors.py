#! /usr/bin/env python

import argparse
import parser
import json
import numpy as np
import json

import ROOT as R
R.PyConfig.IgnoreCommandLineOptions = True
R.gROOT.Reset()
R.gROOT.SetBatch(True)

parser = argparse.ArgumentParser(description='Create TH1s with btagging scale factors and errors, from the framework JSON')

parser.add_argument('-l', help='JSON file for light jets', required=True)
parser.add_argument('-b', help='JSON file for b jets', required=True)
parser.add_argument('-c', help='JSON file for c jets', required=True)
parser.add_argument('-o', '--output', help='Output file', required=True)


options = parser.parse_args()

pt_binning = np.linspace(20, 1000, 400)
pt_binning = np.append(pt_binning, 6000)
n_bins = len(pt_binning) - 1

flavours = ["l", "c", "b"]

def find_bin(binning, x):
    if x < binning[0]:
        return 0
    if x >= binning[-1]:
        return -1
    for i in range(len(binning)):
        if x >= binning[i] and x < binning[i+1]:
            return i

# Assumes Pt bins are along "y" axis
# And Pt is the only variable

out_file = R.TFile.Open(options.output, "recreate")

for flav in flavours:
    with open(getattr(options, flav)) as file:
        this_sf = R.TH1F("btag_sf_" + flav, "", n_bins, pt_binning)
        this_sf_err = R.TH1F("btag_sf_error_" + flav, "", n_bins, pt_binning)

        data = json.load(file)
        json_binning = data["binning"]["y"]
        x_max = json_binning[-1]
        x_min = json_binning[0]

        pt_bins_entries = [ entry["values"][0] for entry in data["data"][0]["values"] ]

        formulas_sf = [ R.TFormula("sf_" + flav, entry["value"]) for entry in pt_bins_entries ]
        # Assumes error are symmetric
        formulas_sf_err = [ R.TFormula("sf_error_" + flav, entry["error_low"]) for entry in pt_bins_entries ]

        for i in range(1, n_bins + 1):
            pt = this_sf.GetBinCenter(i)
            in_range = True
            if pt < x_min:
               in_range = False
               pt = x_min + 1
            if pt >= x_max:
               in_range = False
               pt = x_max - 1
            
            json_bin = find_bin(json_binning, pt)

            nominal = formulas_sf[json_bin].Eval(pt)
            this_sf.SetBinContent(i, nominal)
            
            error = abs(nominal - formulas_sf_err[json_bin].Eval(pt))
            if in_range:
               this_sf_err.SetBinContent(i, error)
            else:
               this_sf_err.SetBinContent(i, 2 * error)

        this_sf.Write()
        this_sf_err.Write()

out_file.Close()
