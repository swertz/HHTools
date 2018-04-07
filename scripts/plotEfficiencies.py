#! /usr/bin/env python

from __future__ import division

import ROOT
import argparse
import copy
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from scipy.interpolate import Akima1DInterpolator
import numpy as np

from cp3_llbb.CommonTools.HistogramTools import TFileWrapper
from cp3_llbb.CommonTools.CMSStyle import applyStyle

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input_dir")
parser.add_argument("-c", "--choice", choices=["spin0", "spin2", "kl"])
args = parser.parse_args()

def check_nonres(points):
    cum = []
    ret = []
    for p in points:
        ratio = p[0]/p[1]
        if ratio not in cum:
            cum.append(ratio)
            ret.append(p)
    return ret

nonres = check_nonres([ (kl, kt) for kl in [-20, -5, 0, 1, 2.4, 3.8, 5, 20] for kt in [0.5, 1, 1.75, 2.5] ])
nonres_names = ["{:.2f}_{:.2f}".format(p[0], p[1]).replace(".", "p").replace("-", "m") for p in sorted(nonres, key=lambda p: p[0]/p[1]) if abs(p[0]/p[1]) <= 20 ]


values = {
    #"spin0": [260, 400, 900],
    "spin0": [260, 270, 300, 350, 400, 450, 500, 550, 600, 650, 750, 800, 900],
    "spin2": [260, 270, 300, 350, 400, 450, 500, 550, 600, 650, 700, 800, 900],
    "kl": sorted([ kl/kt for (kl, kt) in nonres if abs(kl/kt) <= 20 ])
}

file_names = {
    "spin0": [ "GluGluToRadionToHHTo2B2VTo2L2Nu_M-{}_narrow_Summer16MiniAODv2_v5.0.1+80X_HHAnalysis_2017-03-01.v0_histos.root".format(m) for m in values["spin0"] ],
    "spin2": [ "GluGluToBulkGravitonToHHTo2B2VTo2L2Nu_M-{}_narrow_Summer16MiniAODv2_v5.0.1+80X_HHAnalysis_2017-03-01.v0_histos.root".format(m) for m in values["spin2"] ],
    "kl": [ "GluGluToHHTo2B2VTo2L2Nu_point_{}_13TeV-madgraph_v5.0.1+80X_HHAnalysis_2017-03-01.v0_histos.root".format(k) for k in nonres_names ]
}

titles_choices = {
    "spin0": "Spin 0 - ",
    "spin2": "Spin 2 - ",
    "kl": ""
}

stages = ["acceptance", "trigger", "b tagging", "$m_{ll} < 76$ GeV"]

stage_dict = {}
for s in stages:
    stage_dict[s] = [0]*len(values[args.choice])

eff_flav = {}
flavs = ["mumu", "emu", "ee", "all"]
for f in flavs:
    eff_flav[f] = copy.deepcopy(stage_dict)

titles_flavs = {
    "mumu": "$\mu^+\mu^-$",
    "emu": "$\mu^{\pm}e^{\mp}$",
    "ee": "$e^+e^-$"
}

for i,v in enumerate(values[args.choice]):
    print("Handling v={}".format(v))

    _tf = TFileWrapper.Open(file_names[args.choice][i])
    if not _tf or _tf.IsZombie():
        print("Could not open file")
        continue
    tree = _tf.Get("t")
    evt_wgt_sum = _tf.Get("event_weight_sum").GetVal()

    denom = evt_wgt_sum

    for event in tree:
        if event.isMuMu:
            flav = "mumu"
        if event.isElMu or event.isMuEl:
            flav = "emu"
        if event.isElEl:
            flav = "ee"

        wgt = event.event_pu_weight * event.sample_weight * event.llidiso
        eff_flav[flav]["acceptance"][i] += wgt

        wgt *= event.trigeff
        eff_flav[flav]["trigger"][i] += wgt

        if event.is_llbb:
            wgt *= event.jjbtag_heavy * event.jjbtag_light
            eff_flav[flav]["b tagging"][i] += wgt

            if event.ll_M < 76:
                eff_flav[flav]["$m_{ll} < 76$ GeV"][i] += wgt

    for k in stages:
        eff_flav["all"][k][i] = eff_flav["mumu"][k][i] + eff_flav["emu"][k][i] + eff_flav["ee"][k][i]
   
    for k in stages:
        for f in flavs:
            eff_flav[f][k][i] /= denom

    _tf.Close()

for f in flavs:
    fig = plt.figure(1, figsize=(6, 6), dpi=300)
    fig.clear()

    # Create an axes instance
    ax = fig.add_subplot(111)
    if f == "all":
        ax.text(0.62, 0.94, titles_choices[args.choice] + "all channels", transform=ax.transAxes)
    else:
        ax.text(0.6, 0.94, titles_choices[args.choice] + titles_flavs[f] + " channel", transform=ax.transAxes)

    handles = []
    for k in stages:
        x = values[args.choice]
        effs = eff_flav[f][k]
        if args.choice == "kl":
            ax.plot([1,1], [0,1], "black", ls="--")
        xnew = np.linspace(min(x), max(x), 100)
        smoother = Akima1DInterpolator(x, effs)
        h, = ax.plot(xnew, smoother(xnew), "--", label=k, lw=2)
        handles.append(h)

    ax.margins(0.05)

    if args.choice == "kl":
        ax.set_xlabel("$\kappa_{\lambda} / \kappa_{t}$")
        ax.set_xlim([-20,20])
    else:
        ax.set_xlabel("$m_{X}$")
    ax.set_ylabel("Signal efficiency")

    if args.choice == "kl":
        if f == "all":
            ax.set_ylim([0, 0.3])
        elif f == "emu":
            ax.set_ylim([0, 0.1])
        else:
            ax.set_ylim([0, 0.1])
    else:
        if f == "all":
            ax.set_ylim([0, 0.3])
        elif f == "emu":
            ax.set_ylim([0, 0.2])
        else:
            ax.set_ylim([0, 0.1])

    ax.grid(True)

    fig.set_tight_layout(True)

    ax.legend(handles, stages, loc='upper left', numpoints=1, frameon=False)

    applyStyle(fig, ax, lumi=None, extra='Simulation')

    fig.savefig(args.choice + "_" + f + ".pdf")

    plt.close()




