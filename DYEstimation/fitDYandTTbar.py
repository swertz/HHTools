#!/usr/bin/env python

import argparse
import os

def csv_list(string):
    return string.split(',')

def get_args():
    parser = argparse.ArgumentParser(description='Compute different flavour fractions from histograms', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--dy', nargs='+', help='Input ROOT files for DY', required=True)
    parser.add_argument('--bkg', nargs='+', help='Input ROOT files for other backgrounds', required=True)
    parser.add_argument('--data', nargs='+', help='Input ROOT files for data', required=True)
    parser.add_argument('-o', '--output', help='Output folder for validation')
    parser.add_argument('--stage', help='Mll stage', default='no_cut')
    parser.add_argument('--btag', help='Btag stage', default='nobtag')

    options = parser.parse_args()

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

def fitContributions(data, processes, names, hist_name, lumi, output=None):
    histos_mc = []
    for process in processes:
        _h = add_histos( [ getHistogramsFromFileRegex(f, "^" + hist_name + "$").values()[0] for f in process ] )
        check_histo(_h)
        _h.Scale(lumi)
        histos_mc.append(_h)

    prefit_mc = []
    prefit_total = 0
    bins = (1, histos_mc[0].GetNbinsX())
    #bins = (histos_mc[0].GetXaxis().FindFixBin(60), histos_mc[0].GetXaxis().FindFixBin(250))
    print("Using bins: {}".format(bins))
    
    for i in range(len(histos_mc)):
        _h = histos_mc[i]
        _int = _h.Integral(*bins)
        prefit_mc.append(_int)
        prefit_total += _int
        print("Pre-fit yield of process {}: {:.2f}".format(names[i], _int))
    print("Total yield pre-fit: {:.2f}".format(prefit_total))

    mc = ROOT.TObjArray(len(histos_mc))
    for _h in histos_mc:
        mc.Add(_h)
    
    data = add_histos( [ getHistogramsFromFileRegex(f, "^" + hist_name + "$").values()[0] for f in data ] )

    data_total = data.Integral(*bins)
    print("Total yield data: {:.2f}".format(data_total))

    fit = ROOT.TFractionFitter(data, mc)
    fit.SetRangeX(*bins)
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
        
        postfit_mc = res * data_total
        postfit_total += postfit_mc
        postfit_mc_err = err * data_total
        scale = postfit_mc / prefit_mc[i]
        scale_err = postfit_mc_err / prefit_mc[i]
        
        print("Result {}: {:.2f} +- {:.2f} ==> scale by {:.3f} +- {:.3f}".format(names[i], postfit_mc, postfit_mc_err, scale, scale_err))
    
    print("Total yield post-fit: {}".format(postfit_total))
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
    
    LUMI = 35920

    for flav in ["ElEl", "MuMu"]:
        print("\n\n--- Doing {} ---".format(flav))

        hist_name = hist_template.format(flav=flav, btag=options.btag, stage=options.stage)
        
        fitContributions(options.data, [options.dy, options.bkg], ["dy", "bkg"], hist_name, LUMI, options.output)

