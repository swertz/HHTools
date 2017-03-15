#!/usr/bin/env python

import ROOT
import argparse
from numpy.random import uniform

from cp3_llbb.CommonTools import TFileWrapper

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputs", nargs='+')
args = parser.parse_args()

def correct_jer(h_nominal, h_up, h_down):
    n_bins = h_nominal.GetNcells()
    fuzz_up = uniform(-0.1, 0.1, n_bins)
    fuzz_down = uniform(-0.1, 0.1, n_bins)
    for b in range(n_bins):
        nom = h_nominal.GetBinContent(b)
        up = h_up.GetBinContent(b)
        down = h_down.GetBinContent(b)
        delta = 0.5 * (up + down) - nom
        h_up.SetBinContent(b, up - delta + fuzz_up[b] * abs(up - down))
        h_down.SetBinContent(b, down - delta + fuzz_down[b] * abs(up - down))

for file in args.inputs:
    print("Working on {}...".format(file))
    
    _tf = TFileWrapper.Open(file)
    if not _tf or _tf.IsZombie():
        print("Could not open file")
        continue
    
    _histos = _tf.GetListOfKeys()
    _histos = [ k.GetName() for k in _histos if "TH" in k.GetClassName() ]
    nominal_names = [ n for n in _histos if not "__" in n ]
    nominal_names = [ n for n in nominal_names if ( n + "__jerup" in _histos and n + "__jerdown" in _histos ) ]
    nominal = [ _tf.Get(n) for n in nominal_names ]
    jerup = [ _tf.Get(n + "__jerup") for n in nominal_names ]
    jerdown = [ _tf.Get(n + "__jerdown") for n in nominal_names ]

    for _h in nominal + jerup + jerdown:
        _h.SetDirectory(0)

    _tf.Close()

    for i in range(len(nominal)):
        correct_jer(nominal[i], jerup[i], jerdown[i])

    _tf = ROOT.TFile.Open(file, "update")
    for _h in jerup + jerdown:
        _h.Write("", ROOT.TObject.kOverwrite)
    _tf.Close()
