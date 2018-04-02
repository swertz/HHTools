import os
import plotTools
from common import *
import keras

import matplotlib.pyplot as plt

import CMSStyle
    
output_dir = 'resonantROCcomparison'

inputs = [
        "jj_pt", 
        "ll_pt",
        "ll_M",
        "ll_DR_l_l",
        "jj_DR_j_j",
        "llmetjj_DPhi_ll_jj",
        "llmetjj_minDR_l_j",
        "llmetjj_MTformula",
        "isSF"
        ]

cut = "(91 - ll_M) > 15"

models = {

        'all': {
            #'file': 'hh_resonant_trained_models/2017-01-24_260_300_400_550_650_800_900_dy_estimation_from_BDT_new_prod_on_GPU_deeper_lr_scheduler_100epochs/hh_resonant_trained_model.h5',
            'file': 'hh_resonant_trained_models/2017-07-04_260_270_300_350_400_450_500_550_600_650_750_800_900_latest_march_prod_100epochs_REPLAY/hh_resonant_trained_model.h5',
            'legend': 'Training with all masses,\nevaluated at $m_X=${} GeV',
            'style': '--',
            #'markevery': 0.03,
            'color': '#1f77b4'
            },

        'dedicated': {

            #400: {
            #    'file': 'hh_resonant_trained_models/2017-01-24_400_dy_estimation_from_BDT_new_prod_on_GPU_deeper_100epochs/hh_resonant_trained_model.h5',
            #    'legend': 'Dedicated training for M=400 GeV',
            #    'color': '#ff7f0e',
            #    'no_mass_column': True
            #    },

            #900: {
            #    'file': 'hh_resonant_trained_models/2017-01-24_900_dy_estimation_from_BDT_new_prod_on_GPU_deeper_100epochs/hh_resonant_trained_model.h5',
            #    'legend': 'Dedicated training for M=900 GeV',
            #    'color': '#2ca02c',
            #    'no_mass_column': True
            #    },

            650: {
                #'file': 'hh_resonant_trained_models/2017-02-03_260_300_400_550_800_900_dy_estimation_from_BDT_new_prod_on_GPU_deeper_100epochs/hh_resonant_trained_model.h5',
                'file': 'hh_resonant_trained_models/2017-07-04_260_270_300_350_400_450_500_550_600_750_800_900_latest_march_prod_100epochs_REPLAY/hh_resonant_trained_model.h5',
                'legend': 'Training with all masses except 650 GeV,\nevaluated at $m_X=${} GeV',
                'color': '#d62728',
                'style': ':',
                #'markevery': 0.03,
                'no_mass_column': False
                }

            }

        }

masses = sorted(models['dedicated'].keys())


dataset = DatasetManager(inputs, resonant_weights, cut)
dataset.load_resonant_signal(masses=[masses[0]], add_mass_column=True)
dataset.load_backgrounds(add_mass_column=True)

all_model = keras.models.load_model(models['all']['file'])

#fig = plt.figure(1, figsize=(5, 5))
#ax = fig.add_subplot(111)

#CMSStyle.applyStyle(fig, ax, 35900, 'Simulation')

for index, m in enumerate(masses):

    dataset.load_resonant_signal(masses=[m], add_mass_column=True)
    dataset.update_background_mass_column()

    print("Evaluating predictions for M={}".format(m))

    dedicated_model = keras.models.load_model(models['dedicated'][m]['file'])

    # First, the super model
    all_signal_predictions = dataset.get_signal_predictions(all_model)
    all_background_predictions = dataset.get_background_predictions(all_model)

    ignore_last_columns = 0
    if 'no_mass_column' in models['dedicated'][m] and models['dedicated'][m]['no_mass_column']:
        ignore_last_columns = 1
    dedicated_signal_predictions = dataset.get_signal_predictions(dedicated_model, ignore_last_columns=ignore_last_columns)
    dedicated_background_predictions = dataset.get_background_predictions(dedicated_model, ignore_last_columns=ignore_last_columns)

    print("Done.")

    all_n_signal, _, binning = plotTools.binDataset(all_signal_predictions, dataset.get_signal_weights(), bins=1000, range=[0, 1])

    all_n_background, _, _ = plotTools.binDataset(all_background_predictions, dataset.get_background_weights(), bins=binning)

    dedicated_n_signal, _, _ = plotTools.binDataset(dedicated_signal_predictions, dataset.get_signal_weights(), bins=binning)
    dedicated_n_background, _, _ = plotTools.binDataset(dedicated_background_predictions, dataset.get_background_weights(), bins=binning)

    standalone_fig = plt.figure(1, figsize=(5, 5))
    standalone_ax = standalone_fig.add_subplot(111)

    for a in [standalone_ax]:
    #for a in [ax, standalone_ax]:
        for s, b, style in [(all_n_signal, all_n_background, models['all']), (dedicated_n_signal, dedicated_n_background, models['dedicated'][m])]:
            x, y = plotTools.get_roc(s, b)
            cut = (y > 0.7)
            x, y = x[cut], y[cut]
            a.plot(x, y, style['style'], color=style['color'], lw=2, label=style['legend'].format(m), markevery=style.get('markevery'))

    standalone_ax.set_xlabel("Background efficiency", fontsize='large')
    standalone_ax.set_ylabel("Signal efficiency", fontsize='large')
    standalone_ax.text(0.135, 0.76, r'$X_{spin\ 0} \rightarrow\, HH \rightarrow\, b\bar{b}VV \rightarrow\, b\bar{b}l\nu{}l\nu$')

    standalone_ax.margins(0.05)
    standalone_fig.set_tight_layout(True)

    standalone_ax.legend(loc='lower right', numpoints=1, frameon=False)

    output_name = 'roc_comparison_resonant_all_vs_{}.pdf'.format(m)

    CMSStyle.applyStyle(standalone_fig, standalone_ax, lumi=None, extra='Simulation')
    standalone_fig.savefig(os.path.join(output_dir, output_name))

    standalone_fig.clear()

   
#ax.set_xlabel("Background efficiency", fontsize='large')
#ax.set_ylabel("Signal efficiency", fontsize='large')
#
#ax.margins(0.05)
#fig.set_tight_layout(True)
#
#ax.legend(loc='lower right', numpoints=1, frameon=False)
#
#output_name = 'roc_comparison_resonant.pdf'
#
#fig.savefig(os.path.join(output_dir, output_name))
#print("Comparison plot saved as %r" % os.path.join(output_dir, output_name))
