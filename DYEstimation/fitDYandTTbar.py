#!/usr/bin/env python

import argparse
import os

def csv_list(string):
    return string.split(',')

def get_args():
    parser = argparse.ArgumentParser(description='Compute different flavour fractions from histograms', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-m', '--mc', nargs='+', type=csv_list, help='Input ROOT files for MC -- group files for the same process with commas', required=True)
    parser.add_argument('-n', '--names', nargs='+', help='Names of the MC groups', required=True)
    parser.add_argument('-d', '--data', nargs='+', help='Input ROOT files for data', required=True)
    parser.add_argument('-o', '--output', help='Output folder for validation')
    parser.add_argument('--llbb', help='Do llbb stage', action='store_true')

    options = parser.parse_args()

    assert(len(options.mc) == len(options.names))

    return options

import ROOT
from cp3_llbb.CommonTools.HistogramTools import getHistogramsFromFileRegex

def add_histos(_list):
    for h in _list[1:]:
        _list[0].Add(h)
    return _list[0]

def check_histo(_h):
    for i in range(1, _h.GetNbinsX()):
        if _h.GetBinContent(i) < 0:
            _h.SetBinContent(i, 0)

def fitContributions(data, mc, names, hist_name, lumi, output=None):
    prefit_mc = []
    prefit_total = 0
    
    histos_mc = []
    for group in mc:
        hist_group = []
        for f in group:
            hist_group.append(getHistogramsFromFileRegex(f, "^" + hist_name + "$").values()[0])
        _h = add_histos(hist_group)
        check_histo(_h)
        _h.Scale(lumi)
        prefit_mc.append(_h.Integral())
        prefit_total += prefit_mc[-1]
        histos_mc.append(_h)

    mc = ROOT.TObjArray(len(histos_mc))
    for _h in histos_mc:
        mc.Add(_h)
    
    histos_data = []
    for f in data:
        histos_data.append(getHistogramsFromFileRegex(f, "^" + hist_name + "$").values()[0])

    data = add_histos(histos_data)

    fit = ROOT.TFractionFitter(data, mc)
    status = int(fit.Fit())
    print status

    if status != 0:
        del fit
        raise Exception("Fit did not succeed!")

    postfit_total = 0

    for i in range(len(histos_mc)):
        res = ROOT.Double()
        err = ROOT.Double()
        fit.GetResult(i, res, err)
        postfit_mc = res * data.Integral()
        postfit_total += postfit_mc
        postfit_mc_err = err * data.Integral()
        scale = postfit_mc / prefit_mc[i]
        scale_err = postfit_mc_err / prefit_mc[i]
        print("Result {}: {:.2f} +- {:.2f} ==> scale by {:.3f} +- {:.3f}".format(options.names[i], postfit_mc, postfit_mc_err, scale, scale_err))
    print("Had to scale overall by {:.2f}".format(postfit_total / prefit_total))

    if output is not None:
        c = ROOT.TCanvas(hist_name, hist_name, 800, 800)
        data.Draw("E1P")
        data.SetLineWidth(2)
        data.SetLineColor(ROOT.kBlack)
        data.SetMarkerColor(ROOT.kBlack)
        data.SetMarkerStyle(20)
        fit_plot = fit.GetPlot()
        fit_plot.SetLineWidth(2)
        fit_plot.Draw("histsame")
        c.Print(os.path.join(output, hist_name) + ".pdf")
        c.SetLogy()
        c.Print(os.path.join(output, hist_name) + "_logy.pdf")

    del fit



if __name__ == "__main__":
    options = get_args()

    hist_template = "ll_M_{flav}_hh_llmetjj_HWWleptons_{btag}_cmva_{stage}"
    
    LUMI = 35870

    stage = "no_cut"
    btag = "nobtag"
    flavours = ["ElEl", "MuEl", "MuMu"]

    if options.llbb:
        stage = "mll_peak"
        btag = "btagM"
        flavours = ["ElEl", "MuMu"]

    for flav in flavours:
        print("\n\n--- Doing {} ---".format(flav))

        hist_name = hist_template.format(flav=flav, btag=btag, stage=stage)
        
        fitContributions(options.data, options.mc, options.names, hist_name, LUMI, options.output)

