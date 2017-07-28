import os
import pickle
import json
import copy
import datetime

import plotTools
import matplotlib.pyplot as plt

from common import *

import keras

from hyperopt import hp, Trials, STATUS_OK, STATUS_FAIL, tpe, rand, fmin, space_eval
import hyperopt.pyll.stochastic

from sklearn.model_selection import StratifiedKFold

inputs = [
        "jj_pt", 
        "ll_pt",
        "ll_M",
        "ll_DR_l_l",
        "jj_DR_j_j",
        "llmetjj_DPhi_ll_jj",
        "llmetjj_minDR_l_j",
        "llmetjj_MTformula",
        "llmetjj_MT2",
        "isSF"
        ]

cut = "(91 - ll_M) > 15"

parameters_list = nonresonant_parameters
add_parameters_columns = True

#parameters_list = [(1, 1)]
#add_parameters_columns = False


suffix = "hyperopt_parameterised_MT2"

output_suffix = '{:%Y-%m-%d}_{}'.format(datetime.date.today(), suffix)
output_folder = os.path.join('hh_nonresonant_trained_models', output_suffix)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

callbacks = []

output_model_filename = 'hh_nonresonant_trained_model.h5'
output_model_filename = os.path.join(output_folder, output_model_filename)

output_logs_folder = os.path.join('hh_nonresonant_trained_models', 'logs', output_suffix)

callbacks.append(keras.callbacks.EarlyStopping(monitor='val_loss', patience=10))
callbacks.append(keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5))

dataset = DatasetManager(inputs, nonresonant_weights, cut)
dataset.load_nonresonant_signal(parameters_list=parameters_list, add_parameters_columns=add_parameters_columns, fraction=0.1)
dataset.load_backgrounds(add_parameters_columns=add_parameters_columns)
dataset.split(test_size=0.4)

tried_points = []
all_losses = []
n_tries = 0

def save_results():
    with open(os.path.join(output_folder, 'trials_log.json'), mode='w') as _f:
        json.dump({'points': tried_points, 'losses': all_losses}, _f)


    point_vals = {}
    for p in space['model'].keys() + space['fit'].keys():
        point_vals[p] = []
    for t in ['model', 'fit']:
        for p in space[t].keys():
            for s in tried_points:
                point_vals[p].append(s[t][p])

    def log_range(p):
        if p in ['lr', 'l2_param', 'batch_size']:
            return True
        return False

    def plot_parameter(param_name, values, losses):
        fig = plt.figure(1, figsize=(5, 5), dpi=300)
        ax = fig.add_subplot(111)
        
        if log_range(param_name):
            ax.set_xscale('log')

        ax.semilogy(values, losses, 'x')
        
        ax.set_xlabel(param_name)
        ax.set_ylabel('Expected limit')

        fig.savefig(os.path.join(output_folder, param_name + '.pdf'))

        plt.close()

    def plot_parameter_pair(p1, p2, values, losses, colors='b'):
        fig = plt.figure(1, figsize=(6, 6), dpi=300)
        ax = fig.add_subplot(111)

        areas = np.pi * (0.5 * np.array(losses))**2
        
        if log_range(p1):
            ax.set_xscale('log')
        if log_range(p2):
            ax.set_yscale('log')

        try:
            # No idea why he doesn't like some of the colours
            ax.scatter(values[p1], values[p2], s=areas, c=colors, alpha=0.5)
        except ValueError:
            ax.scatter(values[p1], values[p2], s=areas, alpha=0.5)

        ax.set_xlabel(p1)
        ax.set_ylabel(p2)

        fig.savefig(os.path.join(output_folder, p1 + '_vs_' + p2 + '.pdf'))

        plt.close()

    colors = np.random.random((len(trials.losses())-1,4))
    for i, p1 in enumerate(sorted(point_vals.keys())):
        # skip constants
        if np.unique(point_vals[p1]).size == 1:
            continue
        plot_parameter(p1, point_vals[p1], all_losses)
        for j, p2 in enumerate(sorted(point_vals.keys())):
            if j > i and np.unique(point_vals[p2]).size != 1:
                plot_parameter_pair(p1, p2, point_vals, all_losses, colors)


def get_test_limit(dataset, model, idx=None):
    LUMI = 35900

    if idx is None:
        sig = dataset.test_signal_dataset
        bkg = dataset.test_background_dataset
        sig_w = dataset.test_signal_weights
        bkg_w = dataset.test_background_weights

    else:
        data = dataset.training_dataset[idx]
        weights = dataset.training_weights[idx]
        targets = dataset.training_targets[idx]

        idx_sig = (targets == 1)
        idx_bkg = (targets == 0)

        sig = data[idx_sig]
        bkg = data[idx_bkg]
        sig_w = weights[idx_sig]
        # The training signals are not correctly weighted...
        # Normalise the weights to have a "reasonable" total signal yield,
        # so that the limit-finder converges.
        sig_w /= np.sum(sig_w) * LUMI
        bkg_w = weights[idx_bkg]

    sig_pred = model.predict(sig, batch_size=20000)[:,0]
    bkg_pred = model.predict(bkg, batch_size=20000)[:,0]

    sig_binned = plotTools.binDataset(sig_pred, LUMI * sig_w, bins=50, range=[0,1])
    bkg_binned = plotTools.binDataset(bkg_pred, LUMI * bkg_w, bins=50, range=[0,1])

    return get_median_expected_limit(sig_binned, bkg_binned, guess=100)

def objective_cv(args):
    """Return limit averaged over k-fold cross-validated models,
    on training data only. Test data NOT used."""

    global tried_points
    global all_losses
    global n_tries
    n_tries += 1

    args['fit']['epochs'] = int(args['fit']['epochs'])

    print("\nTry {}: testing model for sampling point: {}".format(n_tries, args))
    
    k_folds = args['k_folds']
    skf = StratifiedKFold(n_splits=k_folds)
    limits = []
    
    for i, (train, test) in enumerate(skf.split(dataset.training_dataset, dataset.training_targets)):
        print("Training on fold {} out of {}...".format(i+1, k_folds))

        model = create_nonresonant_model(**args['model'])

        history = model.fit(
                dataset.training_dataset[train],
                dataset.training_targets[train],
                sample_weight=dataset.training_weights[train],
                verbose=False,
                validation_data=(dataset.training_dataset[test], dataset.training_targets[test], dataset.training_weights[test]),
                callbacks=callbacks,
                **args['fit'])

        limit = get_test_limit(dataset, model, test)
    
        if limit is not None:
            print("... Limit is {}".format(limit))
            limits.append(limit)
            
            plotTools.draw_keras_history(history, output_dir=output_folder, output_name="loss_try_{}_fold_{}_limit_{}.pdf".format(n_tries, i, limit))
        else:
            print("Try {} failed: Could not compute a limit!".format(n_tries))
            return {'status': STATUS_FAIL}
    
    limit = np.mean(limits)

    tried_points.append(args)
    all_losses.append(limit)
    save_results()

    best_so_far = np.min(all_losses)

    print("Try {}: K-fold limits: {} -- Average expected limit: {} -- Best so far: {}".format(n_tries, limits, limit, best_so_far))

    return {'loss': limit, 'status': STATUS_OK}


def objective(args):
    """Return limit computed on test set with model trained on training set."""
    
    global tried_points
    global all_losses
    global n_tries
    n_tries += 1

    args['fit']['epochs'] = int(args['fit']['epochs'])

    print("\nTry {}: testing model for sampling point: {}".format(n_tries, args))
    
    model = create_nonresonant_model(**args['model'])

    history = model.fit(
            dataset.training_dataset,
            dataset.training_targets,
            sample_weight=dataset.training_weights,
            verbose=False,
            validation_data=(dataset.testing_dataset, dataset.testing_targets, dataset.testing_weights),
            callbacks=callbacks,
            **args['fit'])

    limit = get_test_limit(dataset, model)

    if limit is None:
        return {'status': STATUS_FAIL}

    tried_points.append(args)
    all_losses.append(limit)
    save_results()

    plotTools.draw_keras_history(history, output_dir=output_folder, output_name="loss_try_{}_limit_{}.pdf".format(n_tries, limit))

    best_so_far = np.min(all_losses)

    print("Try {}: Expected limit: {} -- Best so far: {}".format(n_tries, limit, best_so_far))

    return {'loss': limit, 'status': STATUS_OK}

### Define the space over which the training is to be optimised

space = {
            'k_folds': 2,
            'model': {
                'n_inputs': len(inputs) + 2 * add_parameters_columns,
                'n_neurons': 100, #hp.choice('n_neurons', [20, 50, 100]),
                'n_hidden_layers': 5, #2 + hp.randint('n_hidden_layers', 4),
                'lr': hp.loguniform('lr', np.log(1e-4), np.log(1e-2)),
                'do_dropout': hp.choice('do_dropout', [0, 1]),
                'dropout': hp.uniform('dropout', 0.3, 0.7),
                'batch_norm': True, #hp.choice('batch_norm', [0, 1]),
                #'l2_param': hp.loguniform('l2_param', np.log(1e-8), np.log(1e-4)),
                },
            'fit':  {
                'batch_size': hp.choice('batch_size', [512, 1024, 2048, 4096]),
                'epochs': 200, #hp.quniform('epochs', 20, 150, 1)
                }
        }

### Actually start the minimisation of the objective

trials = Trials()
#print hyperopt.pyll.stochastic.sample(space)

best_run = fmin(objective_cv, space=space, algo=tpe.suggest, max_evals=50, trials=trials, verbose=True)

print("Best performing hyperparameters:")
best_run = space_eval(space, best_run)
print(best_run)

print("Losses:")
print(trials.losses())

save_results()

with open(os.path.join(output_folder, 'trials_log.json'), mode='w') as _f:
    json.dump({'points': tried_points, 'losses': all_losses, 'best_run': best_run}, _f)


print("Done!")


