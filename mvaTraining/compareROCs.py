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
        # "isSF"
        ]

cut = "(91 - ll_M) > 15"
weight = "event_weight * trigeff * jjbtag_heavy * jjbtag_light * llidiso * pu * dy_nobtag_to_btagM_weight"

dataset = DatasetManager(inputs, weight, cut)
dataset.load_resonant_signal(masses=[650], add_mass_column=True)
dataset.load_backgrounds(add_mass_column=True)
# dataset.split()

models = [
    {
        'file': 'hh_resonant_trained_model_650_with_mass_in_input.h5',
        'legend': 'NN training with M=650 GeV',
        'color': '#8E2800'
    },

    {
        'file': 'hh_resonant_trained_model_400_650_900_with_mass_in_input.h5',
        'legend': 'NN training with M=400, 650, 900 GeV',
        'color': '#468966'
    },

    {
        'file': 'hh_resonant_trained_model_400_900_with_mass_in_input.h5',
        'legend': 'NN training with M=400 and 900 GeV',
        'color': '#FFB03B'
    },
]

fig = plt.figure(1, figsize=(7, 7))
ax = fig.add_subplot(111)

for m in models:
    print("Evaluating predictions from %r" % m['file'])
    model = keras.models.load_model(os.path.join('trained_models', m['file']))

    print("Signal...")
    signal_predictions = dataset.get_signal_predictions(model)
    print("Background...")
    background_predictions = dataset.get_background_predictions(model)
    print("Done.")

    n_signal, binning = plotTools.binPredictions(signal_predictions, dataset.get_signal_weights(), bins=100, range=[0, 1])
    n_background, _ = plotTools.binPredictions(background_predictions, dataset.get_background_weights(), bins=binning)

    x, y = plotTools.get_roc(n_signal, n_background)
    ax.plot(x, y, '-', color=m['color'], lw=2, label=m['legend'])

   
ax.set_xlabel("Background efficiency", fontsize='large')
ax.set_ylabel("Signal efficiency", fontsize='large')

ax.margins(0.05)
fig.set_tight_layout(True)

ax.legend(loc='lower right', numpoints=1, frameon=False)

output_dir = '.'
output_name = 'roc_comparison.pdf'

fig.savefig(os.path.join(output_dir, output_name))
print("Comparison plot saved as %r" % os.path.join(output_dir, output_name))
