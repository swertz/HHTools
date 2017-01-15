import glob
import os
import pickle
import gzip

import plotTools
import datetime

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
        "isSF"
        ]

cut = "(91 - ll_M) > 15"
# FIXME: Put b-tagging SFs back once they are correct
weight = {
            # '__base__': "event_weight * trigeff * jjbtag_heavy * jjbtag_light * llidiso * pu",
            '__base__': "event_weight * trigeff * llidiso * pu",
            'DYJetsToLL_M.*': "dy_nobtag_to_btagM_weight"
}

add_mass_column = True

signal_masses = [400, 650, 900]

suffix = "dy_estimation_from_BDT"
output_suffix = '{:%Y-%m-%d}_{}_{}'.format(datetime.date.today(), '_'.join([str(x) for x in signal_masses]), suffix)
output_folder = os.path.join('hh_resonant_trained_models', output_suffix)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

dataset = DatasetManager(inputs, weight, cut)
dataset.load_resonant_signal(masses=signal_masses, add_mass_column=add_mass_column, fraction=1)
dataset.load_backgrounds(add_mass_column=add_mass_column)
dataset.split()

training_dataset, training_targets = dataset.get_training_combined_dataset_and_targets()
training_weights = dataset.get_training_combined_weights()

testing_dataset, testing_targets = dataset.get_testing_combined_dataset_and_targets()
testing_weights = dataset.get_testing_combined_weights()

callbacks = []

output_model_filename = 'hh_resonant_trained_model.h5'
output_model_filename = os.path.join(output_folder, output_model_filename)

callbacks.append(keras.callbacks.ModelCheckpoint(output_model_filename, monitor='val_loss', verbose=False, save_best_only=True, mode='auto'))

output_logs_folder = os.path.join('hh_resonant_trained_models', 'logs', output_suffix)
callbacks.append(keras.callbacks.TensorBoard(log_dir=output_logs_folder, histogram_freq=1, write_graph=True, write_images=False))

training = True

# Load model
if training:
    n_inputs = len(inputs)
    if add_mass_column:
        n_inputs += 1
    model = create_resonant_model(n_inputs)

    history = model.fit(training_dataset, training_targets, sample_weight=training_weights, batch_size=2000, nb_epoch=400, verbose=True, validation_data=(testing_dataset, testing_targets, testing_weights), callbacks=callbacks)

    plotTools.draw_keras_history(history, output_dir=output_folder, output_name="loss.pdf")

    # Save history
    print("Saving model training history...")
    output_history_filename = 'hh_resonant_trained_model_history.pklz'
    output_history_filename = os.path.join(output_folder, output_history_filename)
    with gzip.open(output_history_filename, 'wb') as f:
        pickle.dump(history.history, f)
    print("Done.")

model = keras.models.load_model(output_model_filename)

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
             output_dir=output_folder, output_name="nn_output.pdf")

plotTools.draw_roc(n_signal, n_background, output_dir=output_folder, output_name="roc_curve.pdf")

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
                 output_dir=output_folder, output_name="nn_output_fixed_M%d.pdf" % (m))

    plotTools.draw_roc(n_signal, n_background, output_dir=output_folder, output_name="roc_curve_fixed_M%d.pdf" % (m))
print("Done")
