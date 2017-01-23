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
            'file': 'hh_nonresonant_trained_models/2017-01-24_dy_estimation_from_BDT_new_prod_deeper_lr_scheduler_st_0p005_100epochs/hh_nonresonant_trained_model.h5',
            'legend': 'Training with all parameters at {}',
            'color': '#1f77b4'
            },

        'dedicated': {

            (1, 1): {
                'file': 'hh_nonresonant_trained_models/2017-01-25_dy_estimation_from_BDT_new_prod_deeper_lr_scheduler_st_0p005_onlySM_100epochs/hh_nonresonant_trained_model.h5',
                'legend': 'Dedicated training for {}',
                'color': '#ff7f0e',
                'no_mass_column': True
                },

           (-20, 0.5): {
                'file': 'hh_nonresonant_trained_models/2017-01-25_dy_estimation_from_BDT_new_prod_deeper_lr_scheduler_st_0p005_only-20_0p5_100epochs/hh_nonresonant_trained_model.h5',
                'legend': 'Dedicated training for {}',
                'color': '#2ca02c',
                'no_mass_column': True
                }

            }

        }

parameters = sorted(models['dedicated'].keys(), key=lambda c: c[0])


dataset = DatasetManager(inputs, nonresonant_weights, cut)
dataset.load_nonresonant_signal(parameters_list=nonresonant_parameters, add_parameters_columns=True)
dataset.load_backgrounds(add_parameters_columns=True)

all_model = keras.models.load_model(models['all']['file'])

fig = plt.figure(1, figsize=(7, 7))
ax = fig.add_subplot(111)


line_styles = ['-', '--']

for index, p in enumerate(parameters):

    dataset.load_nonresonant_signal(parameters_list=[p], add_parameters_columns=True)
    dataset.update_background_parameters_column()

    print("Evaluating predictions for {}".format(format_nonresonant_parameters(p)))

    dedicated_model = keras.models.load_model(models['dedicated'][p]['file'])

    # First, the super model
    all_signal_predictions = dataset.get_signal_predictions(all_model)
    all_background_predictions = dataset.get_background_predictions(all_model)

    dedicated_signal_predictions = dataset.get_signal_predictions(dedicated_model, ignore_last_columns=2)
    dedicated_background_predictions = dataset.get_background_predictions(dedicated_model, ignore_last_columns=2)

    print("Done.")

    all_n_signal, _, binning = plotTools.binDataset(all_signal_predictions, dataset.get_signal_weights(), bins=50, range=[0, 1])

    all_n_background, _, _ = plotTools.binDataset(all_background_predictions, dataset.get_background_weights(), bins=binning)

    dedicated_n_signal, _, _ = plotTools.binDataset(dedicated_signal_predictions, dataset.get_signal_weights(), bins=binning)
    dedicated_n_background, _, _ = plotTools.binDataset(dedicated_background_predictions, dataset.get_background_weights(), bins=binning)

    for s, b, style in [(all_n_signal, all_n_background, models['all']), (dedicated_n_signal, dedicated_n_background, models['dedicated'][p])]:
        x, y = plotTools.get_roc(s, b)
        ax.plot(x, y, line_styles[index], color=style['color'], lw=2, label=style['legend'].format(format_nonresonant_parameters(p)))

   
ax.set_xlabel("Background efficiency", fontsize='large')
ax.set_ylabel("Signal efficiency", fontsize='large')

ax.margins(0.05)
fig.set_tight_layout(True)

ax.legend(loc='lower right', numpoints=1, frameon=False)

output_dir = '.'
output_name = 'roc_comparison_nonresonant.pdf'

fig.savefig(os.path.join(output_dir, output_name))
print("Comparison plot saved as %r" % os.path.join(output_dir, output_name))
