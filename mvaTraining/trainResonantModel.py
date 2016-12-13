import glob
import os

import plotTools

from common import *

import keras


inputs = [
        "jj_pt", 
        "ll_pt",
        "ll_M",
        "ll_DR_l_l",
        "jj_DR_j_j",
        "llmetjj_DPhi_ll_jj",
        "llmetjj_minDR_l_j",
        "llmetjj_MTformula",
        ]

cut = "(91 - ll_M) > 15"
weight = "event_weight * trigeff * jjbtag_heavy * jjbtag_light * llidiso * pu * nobtag_to_btagM_weight"
# weight = "event_weight"

add_mass_column = True

signal_masses = [650]

dataset = DatasetManager(inputs, weight, cut)
dataset.load_resonant_signal(masses=signal_masses, add_mass_column=add_mass_column)
dataset.load_backgrounds(add_mass_column=add_mass_column)
dataset.split()

training_dataset, training_targets = dataset.get_training_combined_dataset_and_targets()
training_weights = dataset.get_training_combined_weights()

testing_dataset, testing_targets = dataset.get_testing_combined_dataset_and_targets()
testing_weights = dataset.get_testing_combined_weights()

callbacks = []

output_folder = 'trained_models'
output_suffix = "%s%s" % ('_'.join([str(x) for x in signal_masses]), '_with_mass_in_input' if add_mass_column else '')

output_model_filename = 'hh_resonant_trained_model_%s.h5' % (output_suffix)
output_model_filename = os.path.join(output_folder, output_model_filename)

callbacks.append(keras.callbacks.ModelCheckpoint(output_model_filename, monitor='val_loss', verbose=False, save_best_only=True, mode='auto'))
callbacks.append(keras.callbacks.TensorBoard(log_dir=os.path.join('trained_models', 'logs', output_suffix), histogram_freq=1, write_graph=True, write_images=False))

training = True

# Load model
if training:
    n_inputs = len(inputs)
    if add_mass_column:
        n_inputs += 1
    model = create_resonant_model(n_inputs)

    history = model.fit(training_dataset, training_targets, sample_weight=training_weights, batch_size=1000, nb_epoch=200, verbose=True, validation_data=(testing_dataset, testing_targets, testing_weights), callbacks=callbacks)

model = keras.models.load_model(output_model_filename)

print("Evaluating model performances...")

training_signal_weights, training_background_weights = dataset.get_training_weights()
testing_signal_weights, testing_background_weights = dataset.get_testing_weights()

training_signal_predictions, testing_signal_predictions = dataset.get_signal_predictions(model)
training_background_predictions, testing_background_predictions = dataset.get_background_predictions(model)

print("Done")

print("Doing some plots...")
n_background, n_signal = plotTools.drawNNOutput(training_background_predictions, testing_background_predictions,
             training_signal_predictions, testing_signal_predictions,
             training_background_weights, testing_background_weights,
             training_signal_weights, testing_signal_weights,
             output_dir=output_folder, output_name="nn_output_%s.pdf" % output_suffix)

plotTools.draw_roc(n_signal, n_background, output_dir=output_folder, output_name="roc_curve_%s.pdf" % output_suffix)
print("Done")
