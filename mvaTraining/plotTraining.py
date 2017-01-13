import os
import re
import plotTools

from common import *

import keras

import argparse

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

add_mass_column = True
signal_masses = [400, 650, 900]

cut = "(91 - ll_M) > 15"
weight = "event_weight * trigeff * jjbtag_heavy * jjbtag_light * llidiso * pu * dy_nobtag_to_btagM_weight"

parser = argparse.ArgumentParser(description='Plot NN output and ROC curve of a training.')
parser.add_argument('input', metavar='FILE', help='Trained model H5 file', type=str)

args = parser.parse_args()

model = keras.models.load_model(args.input)

# Extract suffix from input name
# input = hh_(non)resonant_trained_model_<suffix>.h5
pattern = re.compile(r"hh_(?:non)?resonant_trained_model_(.*)\.h5$")
groups = pattern.search(args.input)

suffix = groups.group(1)

output_folder = '.'

dataset = DatasetManager(inputs, weight, cut)
dataset.load_resonant_signal(masses=signal_masses, add_mass_column=add_mass_column)
dataset.load_backgrounds(add_mass_column=add_mass_column)
dataset.split()

training_dataset, training_targets = dataset.get_training_combined_dataset_and_targets()
training_weights = dataset.get_training_combined_weights()

testing_dataset, testing_targets = dataset.get_testing_combined_dataset_and_targets()
testing_weights = dataset.get_testing_combined_weights()

print("Evaluating model performances...")

training_signal_weights, training_background_weights = dataset.get_training_weights()
testing_signal_weights, testing_background_weights = dataset.get_testing_weights()

training_signal_predictions, testing_signal_predictions = dataset.get_training_testing_signal_predictions(model)
training_background_predictions, testing_background_predictions = dataset.get_training_testing_background_predictions(model)

print("Done")

print("Doing some plots...")
n_background, n_signal = plotTools.drawNNOutput(training_background_predictions, testing_background_predictions,
             training_signal_predictions, testing_signal_predictions,
             training_background_weights, testing_background_weights,
             training_signal_weights, testing_signal_weights,
             output_dir=output_folder, output_name="nn_output_all_%s.pdf" % suffix)

plotTools.draw_roc(n_signal, n_background, output_dir=output_folder, output_name="roc_curve_all_%s.pdf" % suffix)

# Split by training mass
for m in signal_masses:
    training_signal_dataset, training_background_dataset = dataset.get_training_datasets()
    testing_signal_dataset, testing_background_dataset = dataset.get_testing_datasets()

    training_signal_mask = training_signal_dataset[:,-1] == m
    training_background_mask = training_background_dataset[:,-1] == m
    testing_signal_mask = testing_signal_dataset[:,-1] == m
    testing_background_mask = testing_background_dataset[:,-1] == m

    mass_training_background_predictions = training_background_predictions[training_background_mask]
    mass_training_signal_predictions = training_signal_predictions[training_signal_mask]
    mass_training_background_weights = training_background_weights[training_background_mask]
    mass_training_signal_weights = training_signal_weights[training_signal_mask]

    mass_testing_background_predictions = testing_background_predictions[testing_background_mask]
    mass_testing_signal_predictions = testing_signal_predictions[testing_signal_mask]
    mass_testing_background_weights = testing_background_weights[testing_background_mask]
    mass_testing_signal_weights = testing_signal_weights[testing_signal_mask]

    n_background, n_signal = plotTools.drawNNOutput(
                 mass_training_background_predictions, mass_testing_background_predictions,
                 mass_training_signal_predictions, mass_testing_signal_predictions,
                 mass_training_background_weights, mass_testing_background_weights,
                 mass_training_signal_weights, mass_testing_signal_weights,
                 output_dir=output_folder, output_name="nn_output_M%d_%s.pdf" % (m, suffix))

    plotTools.draw_roc(n_signal, n_background, output_dir=output_folder, output_name="roc_curve_M%d_%s.pdf" % (m, suffix))

print("Done")
