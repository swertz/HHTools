import glob
import os
import pickle
import gzip
import datetime
from timeit import default_timer as timer

import plotTools

from common import *

import keras

from keras import backend as K

class LossHistory(keras.callbacks.Callback):
    def __init__(self, name):
        self.name = name
        self.history = {'loss': [], 'val_loss': []}

    def on_epoch_end(self, batch, logs={}):
        self.history['loss'].append(logs.get('loss'))
        self.history['val_loss'].append(logs.get('val_loss'))

class BatchLossHistory(keras.callbacks.Callback):
    def __init__(self, name):
        self.name = name
        self.history = {'loss': []}

    def on_batch_end(self, batch, logs={}):
        self.history['loss'].append(logs.get('loss'))

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
independent = "jj_M"

cut = "(91 - ll_M) > 15"

# parameters_list = nonresonant_parameters
# add_parameters_columns = True

parameters_list = [(1, 1)]
add_parameters_columns = False

suffix = "test_LSMI_2D_alternate_SR"

output_suffix = '{:%Y-%m-%d}_{}'.format(datetime.date.today(), suffix)
output_folder = os.path.join('hh_nonresonant_trained_models', output_suffix)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

dataset = DatasetManager(inputs, nonresonant_weights, cut, extra_variables=[independent])
dataset.load_nonresonant_signal(parameters_list=parameters_list, add_parameters_columns=add_parameters_columns, fraction=1)
dataset.load_backgrounds(add_parameters_columns=add_parameters_columns)
dataset.split()


def to_array(a):
    return a.view( (np.float32, len(a.dtype.names)) )

training_features = dataset.training_dataset
training_independent = np.reshape(dataset.training_extra_dataset, (-1,1))
training_targets = dataset.training_targets 
training_weights = dataset.get_training_combined_weights()

testing_features = dataset.testing_dataset
testing_independent = np.reshape(dataset.testing_extra_dataset, (-1,1))
testing_targets = dataset.testing_targets 
testing_weights = dataset.get_testing_combined_weights()

output_model_filename = 'hh_nonresonant_trained_model.h5'
output_model_filename = os.path.join(output_folder, output_model_filename)

output_model_lsmi_filename = 'hh_nonresonant_trained_model_lsmi.h5'
output_model_lsmi_filename = os.path.join(output_folder, output_model_lsmi_filename)

#callbacks.append(keras.callbacks.ModelCheckpoint(output_model_filename, monitor='val_loss', verbose=False, save_best_only=True, mode='auto'))
history_discr = LossHistory("discr")
history_discr_batched = LossHistory("discr_batched")
callbacks_discr = [ history_discr ]
callbacks_discr.append(keras.callbacks.EarlyStopping(monitor='val_loss', patience=20))
callbacks_discr.append(keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5))

history_lsmi = BatchLossHistory("lsmi")
callbacks_lsmi = [ history_lsmi ]
callbacks_lsmi.append(keras.callbacks.EarlyStopping(monitor='val_loss', patience=3))
callbacks_lsmi.append(keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3))

output_logs_folder = os.path.join('hh_nonresonant_trained_models', 'logs', output_suffix)

training = True
training_time = None

skip_pretraining = False

n_inputs = len(inputs)
if add_parameters_columns:
    n_inputs += 2

params = {
        'n_neurons': 100,
        'n_hidden_layers': 4,
        'lr': 0.001,
        'do_dropout': True,
        'dropout': 0.25,
        'l2_param': 0,
        'batch_norm': True,
        'lamb': 0.01,
        'lsmi_l2': 0.01,
        'sigma_x': 1,
        'sigma_y': 1,
    }

discr, lsmi = create_LSMI_model(n_inputs, **params)
keras.utils.plot_model(discr, to_file=os.path.join(output_folder, 'discr_model.png'))
keras.utils.plot_model(lsmi, to_file=os.path.join(output_folder, 'lsmi_model.png'))

start_time = timer()

batch_size = 5000
nb_epoch = 50

print("Training discriminator")

discr.fit(
        training_features,
        training_targets,
        sample_weight=training_weights,
        batch_size=batch_size,
        epochs=nb_epoch,
        verbose=True,
        validation_data=(testing_features, testing_targets, testing_weights),
        callbacks=callbacks_discr)


batch_size = 1000
nb_epoch = 2

print("Training LSMI")

n_loop = len(training_features) / (batch_size)
for i in range(n_loop):
    print("Loop {} / {}...".format(i, n_loop))

    for j in range(nb_epoch):
        indices = np.random.permutation(len(training_features))[:batch_size]
        lsmi_loss = lsmi.train_on_batch(
            [training_features[indices], training_independent[indices]], 
            training_targets[indices], 
            sample_weight=training_weights[indices])
        history_lsmi.history['loss'].append(lsmi_loss)
    print("LSMI: {}".format(history_lsmi.history['loss'][-1]))

    discr_indices = np.random.permutation(len(training_features))[:200000]
    discr_mjj_SR = ((training_independent[discr_indices] >= 75) & (training_independent[discr_indices] < 140)).ravel()
    discr_mjj_SR_test = ((testing_independent[discr_indices] >= 75) & (testing_independent[discr_indices] < 140)).ravel()
    discr.fit(
        training_features[discr_indices][discr_mjj_SR],
        training_targets[discr_indices][discr_mjj_SR], 
        sample_weight=training_weights[discr_indices][discr_mjj_SR],
        batch_size=5000,
        epochs=1,
        validation_data=(testing_features[discr_indices][discr_mjj_SR_test], testing_targets[discr_indices][discr_mjj_SR_test], testing_weights[discr_indices][discr_mjj_SR_test]),
        callbacks=[history_discr_batched])

#history_lsmi = lsmi.fit(
#    [training_features, training_independent], 
#    training_targets, 
#    sample_weight=training_weights, 
#    batch_size=batch_size,
#    epochs=nb_epoch, 
#    verbose=True,
#    validation_data=([testing_features, testing_independent], testing_targets, testing_weights),
#    callbacks=callbacks_lsmi)

# Save only after the LSMI training, since that modifies the base model's weights
discr.save(output_model_filename)
lsmi.save(output_model_lsmi_filename)

end_time = timer()
training_time = datetime.timedelta(seconds=(end_time - start_time))
    
# Save history
print("Saving model training history...")
for history in [history_discr, history_lsmi, history_discr_batched]:
    plotTools.draw_keras_history(history, output_dir=output_folder, output_name="history_" + history.name + ".pdf")


########################################
##### Re-loading model and evaluate ####
########################################

model = keras.models.load_model(output_model_filename)

export_for_lwtnn(model, output_model_filename)
draw_non_resonant_training_plots(model, dataset, output_folder, split_by_parameters=add_parameters_columns)
draw_nn_vs_independent(model, dataset, np.linspace(0, 400, 20), output_folder)

# Compute limit on test set
sig_pred = model.predict(dataset.test_signal_dataset, batch_size=20000)[:,0]
bkg_pred = model.predict(dataset.test_background_dataset, batch_size=20000)[:,0]

LUMI = 35900

sig_binned = plotTools.binDataset(sig_pred, LUMI * dataset.test_signal_weights, bins=50, range=[0,1])
bkg_binned = plotTools.binDataset(bkg_pred, LUMI * dataset.test_background_weights, bins=50, range=[0,1])

limit = get_median_expected_limit(sig_binned, bkg_binned, guess=10)

print("Expected limit from test set: {} fb".format(limit))

print("All done. Training time: %s" % str(training_time))
