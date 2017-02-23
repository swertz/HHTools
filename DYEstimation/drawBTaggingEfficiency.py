#! /bin/env python

import argparse

import cp3_llbb.CommonTools.CMSStyle

import ROOT as R

R.PyConfig.IgnoreCommandLineOptions = True
R.gROOT.Reset()
R.gROOT.SetBatch(True)

R.gStyle.SetOptStat(0)
R.gStyle.SetOptTitle(0)
R.gStyle.SetPaintTextFormat(".2f")
R.gStyle.SetTextFont(42)

def drawEfficiency(obj):
    # Ignore systematics for the moment
    # if "__" in obj.GetName():
        # return

    c = R.TCanvas("c", "c", 1600, 800)

    h = obj.GetCopyPassedHisto()
    h.Reset()
    h.SetDirectory(0)

    for x in range(1, h.GetNbinsX() + 1):
        for y in range(1, h.GetNbinsY() + 1):
            bin = h.GetBin(x, y)
            eff = obj.GetEfficiency(bin)
            err = max(obj.GetEfficiencyErrorLow(bin), obj.GetEfficiencyErrorUp(bin))

            h.SetBinContent(x, y, eff)
            h.SetBinError(x, y, err)

    h.GetXaxis().SetTitle("p_{T}")
    h.GetYaxis().SetTitle("|#eta|")

    c.SetLogx()
    if "eff_on_q" in obj.GetName() or "eff_on_l" in obj.GetName() or "eff_on_g" in obj.GetName() or "eff_on_n" in obj.GetName():
        c.SetLogz()
    h.SetContour(100)
    h.Draw("colz text err")
    c.SaveAs(obj.GetName() + ".pdf")

parser = argparse.ArgumentParser(description='Draw b-tagging efficiency')
parser.add_argument('input', type=str, metavar='FILE', help='Input file containing efficiencies')

options = parser.parse_args()

f = R.TFile.Open(options.input)
for key in f.GetListOfKeys():
    clazz = R.gROOT.GetClass(key.GetClassName())
    if not clazz.InheritsFrom("TEfficiency"):
        continue

    obj = key.ReadObj()
    drawEfficiency(obj)
