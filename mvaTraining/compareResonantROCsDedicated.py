import os
import plotTools
from common import *
import keras

import matplotlib.pyplot as plt

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
            'file': 'hh_resonant_trained_models/2017-01-24_260_300_400_550_650_800_900_dy_estimation_from_BDT_new_prod_on_GPU_deeper_lr_scheduler_100epochs/hh_resonant_trained_model.h5',
            'legend': 'Training with all masses at M={} GeV',
            'color': '#1f77b4'
            },

        'dedicated': {

            400: {
                'file': 'hh_resonant_trained_models/2017-01-24_400_dy_estimation_from_BDT_new_prod_on_GPU_deeper_100epochs/hh_resonant_trained_model.h5',
                'legend': 'Dedicated training for M=400 GeV',
                'color': '#ff7f0e',
                'no_mass_column': True
                },

            900: {
                'file': 'hh_resonant_trained_models/2017-01-24_900_dy_estimation_from_BDT_new_prod_on_GPU_deeper_100epochs/hh_resonant_trained_model.h5',
                'legend': 'Dedicated training for M=900 GeV',
                'color': '#2ca02c',
                'no_mass_column': True
                },

            650: {
                'file': 'hh_resonant_trained_models/2017-02-03_260_300_400_550_800_900_dy_estimation_from_BDT_new_prod_on_GPU_deeper_100epochs/hh_resonant_trained_model.h5',
                'legend': 'Training with all masses\nexcept 650 GeV, at M={} GeV',
                'color': '#d62728',
                'no_mass_column': False
                }

            }

        }

masses = sorted(models['dedicated'].keys())


dataset = DatasetManager(inputs, resonant_weights, cut)
dataset.load_resonant_signal(masses=[masses[0]], add_mass_column=True)
dataset.load_backgrounds(add_mass_column=True)

all_model = keras.models.load_model(models['all']['file'])

fig = plt.figure(1, figsize=(7, 7))
ax = fig.add_subplot(111)


line_styles = ['-', '--', '-.']

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

    all_n_signal, _, binning = plotTools.binDataset(all_signal_predictions, dataset.get_signal_weights(), bins=50, range=[0, 1])

    all_n_background, _, _ = plotTools.binDataset(all_background_predictions, dataset.get_background_weights(), bins=binning)

    dedicated_n_signal, _, _ = plotTools.binDataset(dedicated_signal_predictions, dataset.get_signal_weights(), bins=binning)
    dedicated_n_background, _, _ = plotTools.binDataset(dedicated_background_predictions, dataset.get_background_weights(), bins=binning)

    standalone_fig = plt.figure(2, figsize=(7, 7))
    standalone_ax = standalone_fig.add_subplot(111)

    for a in [ax, standalone_ax]:
        for s, b, style in [(all_n_signal, all_n_background, models['all']), (dedicated_n_signal, dedicated_n_background, models['dedicated'][m])]:
            x, y = plotTools.get_roc(s, b)
            a.plot(x, y, line_styles[index], color=style['color'], lw=2, label=style['legend'].format(m))

    standalone_ax.set_xlabel("Background efficiency", fontsize='large')
    standalone_ax.set_ylabel("Signal efficiency", fontsize='large')

    standalone_ax.margins(0.05)
    standalone_fig.set_tight_layout(True)

    standalone_ax.legend(loc='lower right', numpoints=1, frameon=False)

    output_dir = '.'
    output_name = 'roc_comparison_resonant_all_vs_{}.pdf'.format(m)

    standalone_fig.savefig(os.path.join(output_dir, output_name))
    standalone_fig.clear()

   
ax.set_xlabel("Background efficiency", fontsize='large')
ax.set_ylabel("Signal efficiency", fontsize='large')

ax.margins(0.05)
fig.set_tight_layout(True)

ax.legend(loc='lower right', numpoints=1, frameon=False)

output_dir = '.'
output_name = 'roc_comparison_resonant.pdf'

fig.savefig(os.path.join(output_dir, output_name))
print("Comparison plot saved as %r" % os.path.join(output_dir, output_name))
