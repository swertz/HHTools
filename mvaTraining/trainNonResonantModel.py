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

class KerasDebugMonitor(keras.callbacks.Callback):
    def __init__(self):
        super(KerasDebugMonitor, self).__init__()

    def _get_learning_rate(self, epoch):
        lr = K.get_value(self.model.optimizer.lr)
        iterations = K.get_value(self.model.optimizer.iterations)
        decay = K.get_value(self.model.optimizer.decay)
        print(decay)
        if decay > 0:
            lr *= (1. / (1. + decay * iterations))

        return lr

    def on_epoch_begin(self, epoch, logs=None):
        if not hasattr(self.model.optimizer, 'lr'):
            raise ValueError('Optimizer must have a "lr" attribute.')
        lr = self._get_learning_rate(epoch)
        print('Epoch %d: learning-rate: %.5e' % (epoch, lr))

    def on_epoch_end(self, epoch, logs=None):
        pass

def lr_scheduler(epoch):
    default_lr = 0.005
    drop = 0.1
    epochs_drop = 50.0
    lr = default_lr * math.pow(drop, min(1, math.floor((1 + epoch) / epochs_drop)))

    return lr

def lr_scheduler_dedicated(epoch):
    default_lr = 0.001
    drop = 0.5
    epochs_drop = 15.0
    lr = default_lr * math.pow(drop, min(1, math.floor((1 + epoch) / epochs_drop)))

    return lr


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

# parameters_list = nonresonant_parameters
parameters_list = nonresonant_parameters
add_parameters_columns = True

# parameters_list = [(-20, 0.5)]
# add_parameters_columns = False

# suffix = "dy_estimation_from_BDT_new_prod_deeper_lr_scheduler_120epochs"
suffix = "latest_march_prod_100epochs"

output_suffix = '{:%Y-%m-%d}_{}'.format(datetime.date.today(), suffix)
output_folder = os.path.join('hh_nonresonant_trained_models', output_suffix)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

dataset = DatasetManager(inputs, nonresonant_weights, cut)
dataset.load_nonresonant_signal(parameters_list=parameters_list, add_parameters_columns=add_parameters_columns, fraction=1)
dataset.load_backgrounds(add_parameters_columns=add_parameters_columns)
dataset.split()

training_dataset, training_targets = dataset.get_training_combined_dataset_and_targets()
training_weights = dataset.get_training_combined_weights()

testing_dataset, testing_targets = dataset.get_testing_combined_dataset_and_targets()
testing_weights = dataset.get_testing_combined_weights()

training_signal_dataset, training_background_dataset = dataset.get_training_datasets()
testing_signal_dataset, testing_background_dataset = dataset.get_testing_datasets()

callbacks = []

output_model_filename = 'hh_nonresonant_trained_model.h5'
output_model_filename = os.path.join(output_folder, output_model_filename)

callbacks.append(keras.callbacks.ModelCheckpoint(output_model_filename, monitor='val_loss', verbose=False, save_best_only=True, mode='auto'))
# callbacks.append(keras.callbacks.ModelCheckpoint(output_model_filename, monitor='loss', verbose=False, save_best_only=True, mode='auto'))

output_logs_folder = os.path.join('hh_nonresonant_trained_models', 'logs', output_suffix)
# callbacks.append(keras.callbacks.TensorBoard(log_dir=output_logs_folder, histogram_freq=1, write_graph=True, write_images=False))

callbacks.append(keras.callbacks.LearningRateScheduler(lr_scheduler))
# callbacks.append(keras.callbacks.LearningRateScheduler(lr_scheduler_dedicated))

training = True
training_time = None

# Load model
if training:
    n_inputs = len(inputs)
    if add_parameters_columns:
        n_inputs += 2
    model = create_nonresonant_model(n_inputs)

    start_time = timer()
    batch_size = 5000
    nb_epoch = 100

    if HAVE_GPU and len(training_dataset) % 2 != 0:
        # Drop the last event
        training_dataset = training_dataset[:-1]
        training_targets = training_targets[:-1]
        training_weights = training_weights[:-1]

    history = model.fit(training_dataset, training_targets, sample_weight=training_weights, batch_size=batch_size,
            nb_epoch=nb_epoch, verbose=True, validation_data=(testing_dataset, testing_targets, testing_weights), callbacks=callbacks)

    end_time = timer()
    training_time = datetime.timedelta(seconds=(end_time - start_time))

    save_training_parameters(output_folder, model,
            batch_size=batch_size, nb_epoch=nb_epoch,
            training_time=str(training_time),
            parameters=parameters_list,
            with_parameters_column=add_parameters_columns,
            inputs=inputs,
            cut=cut,
            weights=nonresonant_weights)

    plotTools.draw_keras_history(history, output_dir=output_folder, output_name="loss.pdf")

    # Save history
    print("Saving model training history...")
    output_history_filename = 'hh_nonresonant_trained_model_history.pklz'
    output_history_filename = os.path.join(output_folder, output_history_filename)
    with gzip.open(output_history_filename, 'wb') as f:
        pickle.dump(history.history, f)
    print("Done.")

model = keras.models.load_model(output_model_filename)

export_for_lwtnn(model, output_model_filename)
draw_non_resonant_training_plots(model, dataset, output_folder, split_by_parameters=add_parameters_columns)

print("All done. Training time: %s" % str(training_time))
