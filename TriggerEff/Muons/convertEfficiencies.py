#! /bin/env python

import ROOT as R

import sys
import numpy as np

import matplotlib
matplotlib.use('agg')

from matplotlib import rc
rc('font', **{'family': 'sans-serif', 'sans-serif':['Arial', 'Helvetica', 'Nimbus Sans L', 'Liberation Sans']})
rc('mathtext', default='regular')

import matplotlib.pyplot as plt

pt_binnings = {
        'DoubleIsoMu17Mu8_IsoMu17leg_pt_eta': [0, 16, 16.5, 16.75, 17, 17.25, 17.5, 18, 20, 25, 30, 40, 50, 60, 80, 120, 200, 500],
        'DoubleIsoMu17TkMu8_IsoMu8legORTkMu8leg_pt_eta': [0, 7.5, 7.75, 8, 8.25, 8.5, 9, 10, 12, 15, 20, 30, 40, 50, 60, 80, 120, 200, 500],
        'XPathIsoMu23leg_pt_eta': [0, 21, 22.5, 22.75, 23, 23.25, 23.5, 24, 25, 27, 30, 40, 50, 60, 80, 120, 200, 500],
        'XPathIsoMu12leg_pt_eta': [0, 11.5, 11.75, 12, 12.25, 12.5, 13, 15, 20, 25, 30, 40, 50, 60, 80, 120, 200, 500],
        'XPathIsoMu8leg_pt_eta': [0, 7.5, 7.75, 8, 8.25, 8.5, 9, 10, 12, 15, 20, 30, 40, 50, 60, 80, 120, 200, 500]
        }

eta_binning = np.asarray([0, 0.9, 1.2, 2.1, 2.4])


def convertToJSON(pt_binning, eta_binning, efficiencies, efficiencies_error_up, efficiencies_error_down, wp):

    json_content = {'dimension': 2, 'variables': ['AbsEta', 'Pt'], 'binning': {'x': eta_binning, 'y': pt_binning}, 'data': [], 'error_type': 'absolute'}
    json_content_data = json_content['data']

    for i in range(0, len(eta_binning) - 1):

        eta_data = {'bin': [eta_binning[i], eta_binning[i + 1]], 'values': []}

        for pt_bin_index in range(0, len(pt_binning) - 1):
            eff = efficiencies[i][pt_bin_index]
            error_up = efficiencies_error_up[i][pt_bin_index]
            error_down = efficiencies_error_down[i][pt_bin_index]

            pt_data = {'bin': [pt_binning[pt_bin_index], pt_binning[pt_bin_index + 1]], 'value': eff, 'error_low': error_down, 'error_high': error_up}

            eta_data['values'].append(pt_data)

        json_content_data.append(eta_data)

    # Save JSON file
    filename = 'Muon_%s.json' % (wp)
    with open(filename, 'w') as j:
        import json
        json.dump(json_content, j, indent=2)
        print("Saved as {}".format(filename))

f = R.TFile.Open(sys.argv[1])
d = f.Get('tpTree')

# output = R.TFile.Open('test.root', 'recreate')

# Loop over all efficiencies
for key in d.GetListOfKeys():

    print("Extracting efficiencies for {}".format(key.GetName()))

    cat = key.ReadObj()

    plots_dir = cat.Get("fit_eff_plots")
    plots = []
    for plot in plots_dir.GetListOfKeys():

        # Expected name
        # pt_PLOT_abseta_bin<X>
        if plot.GetName().startswith("pt_PLOT_abseta_bin"):
            plots.append(plot.ReadObj().GetPrimitive('hxy_fit_eff'))

    data_x = []
    data_y = []
    data_z = []
    data_z_error_up = []
    data_z_error_down = []
    for i, plot in enumerate(plots):
        plot.Sort()
        for j in range(plot.GetN()):
            x = R.Double(0)
            z = R.Double(0)
            plot.GetPoint(j, x, z)
            data_x.append(x)
            data_y.append((eta_binning[i] + eta_binning[i + 1]) / 2)
            data_z.append(z)
            data_z_error_up.append(plot.GetErrorYhigh(j))
            data_z_error_down.append(plot.GetErrorYlow(j))

    # Create a figure instance
    fig = plt.figure(1, figsize=(7, 7), dpi=300)

    # Create an axes instance
    ax = fig.add_subplot(111)

    # ax.margins(0.1, 0.1)

    pt_binning = np.asarray(pt_binnings[key.GetName()])

    # Bin data (simply reshape the data_z array
    z, _, _ = np.histogram2d(data_x, data_y, weights=data_z, bins=(pt_binning, eta_binning))
    z_error_up, _, _ = np.histogram2d(data_x, data_y, weights=data_z_error_up, bins=(pt_binning, eta_binning))
    z_error_down, _, _ = np.histogram2d(data_x, data_y, weights=data_z_error_down, bins=(pt_binning, eta_binning))

    cax = ax.pcolormesh(pt_binning, eta_binning, z.T, cmap='viridis')
    fig.colorbar(cax)

    ax.set_ylim([eta_binning[0], eta_binning[-1]])
    # ax.set_xlim([max(1, pt_binning[0]), pt_binning[-1]])
    ax.set_xlim([5, 40])

    ax.set_xlabel("Muon $p_{T}$")
    ax.set_ylabel("Muon $|\eta|$")

    fig.tight_layout()
    fig.savefig('{}_2D.pdf'.format(key.GetName()))

    plt.close()

    convertToJSON(pt_binning.tolist(), eta_binning.tolist(), z.T, z_error_up.T, z_error_down.T, key.GetName())

    # Draw eff vs pt for each eta bin
    
    fig, ax = plt.subplots()

    ax.grid(True)

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for i in range(len(eta_binning) - 1):
        legend = "${:.2f} < |\eta| < ${:.2f}".format(eta_binning[i], eta_binning[i + 1])
        ax.errorbar((pt_binning[1:] + pt_binning[:-1])/2, z[:, i], yerr=[z_error_down[:, i], z_error_up[:, i]], lw=0, linestyle='none', marker='o', markersize=6, fillstyle='full', c=colors[i], mew=0, label=legend)


    ax.margins(0.1, 0.1)
    ax.legend(loc='best', numpoints=1, frameon=False)

    ax.set_xlabel("Muon $p_{T}$")
    ax.set_ylabel("Efficiency")

    fig.tight_layout()

    ax.set_ylim(0)

    fig.savefig('{}_vs_pt.pdf'.format(key.GetName()))

    plt.close()
