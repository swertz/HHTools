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
from sklearn.metrics import roc_auc_score
from scipy import stats

inputs = [
        "jj_pt", 
        "ll_pt",
        "ll_M",
        "ll_DR_l_l",
        "jj_DR_j_j",
        "llmetjj_DPhi_ll_jj",
        "llmetjj_minDR_l_j",
        "llmetjj_MTformula",
        "jj_M"
        ]
independent = "jj_M > 75 && jj_M < 140"

cut = "(91 - ll_M) > 15"

# parameters_list = nonresonant_parameters
# add_parameters_columns = True

parameters_list = [(1, 1)]
add_parameters_columns = False

suffix = "adversarial_categorical_bkgonly_jj_M_lr"

output_suffix = '{:%Y-%m-%d}_{}'.format(datetime.date.today(), suffix)
output_folder = os.path.join('hh_nonresonant_trained_models', output_suffix)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

dataset = DatasetManager(inputs, nonresonant_weights, cut, extra_variables=[independent])
dataset.load_nonresonant_signal(parameters_list=parameters_list, add_parameters_columns=add_parameters_columns, fraction=1)
dataset.load_backgrounds(add_parameters_columns=add_parameters_columns)
dataset.split(reweight_signal_testing_sample=True)
dataset.normalise_training_weights()
dataset.normalise_testing_weights()


training_features = dataset.training_dataset
training_independent = dataset.training_extra_dataset[:,0].astype(bool)
training_targets = dataset.training_targets 
training_weights = dataset.training_weights

testing_features = dataset.testing_dataset
testing_independent = dataset.testing_extra_dataset[:,0].astype(bool)
testing_targets = dataset.testing_targets 
testing_weights = dataset.testing_weights

#training_independent = (training_independent >= 75) & (training_independent < 140)
#testing_independent = (testing_independent >= 75) & (testing_independent < 140)

# Adversary training only on background!! Set a default value for the nuisance for the signal:
bkg_cut = training_targets[:,0]==0
bkg_cut_test = testing_targets[:,0]==0

callbacks = []

output_model_filename = 'hh_nonresonant_trained_model.h5'
output_model_filename = os.path.join(output_folder, output_model_filename)
discr_weight_file = os.path.join(output_folder, 'discr_weights.h5')
advers_weight_file = os.path.join(output_folder, 'advers_weights.h5')

#callbacks.append(keras.callbacks.ModelCheckpoint(output_model_filename, monitor='val_loss', verbose=False, save_best_only=True, mode='auto'))
callbacks.append(keras.callbacks.EarlyStopping(monitor='val_loss', patience=10))
callbacks.append(keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5))

output_logs_folder = os.path.join('hh_nonresonant_trained_models', 'logs', output_suffix)
#callbacks.append(keras.callbacks.TensorBoard(log_dir=output_logs_folder, histogram_freq=1, write_graph=True, write_images=False))

training_time = None

load_discr = True
load_advers = True
train_discr = False
train_advers = False
train_pivot = False
do_plots = True

# Load model
n_inputs = len(inputs)
if add_parameters_columns:
    n_inputs += 2

lamb = 100.
discr, advers, discr_full, advers_full = create_adversarial_model(n_inputs, 1, lamb)

if load_discr and os.path.exists(discr_weight_file):
    print("\nLoading discriminator weights from previous training!\n")
    discr.load_weights(discr_weight_file)

if load_advers and os.path.exists(advers_weight_file):
    print("\nLoading adversary weights from previous training!\n")
    advers.load_weights(advers_weight_file)

#discr.summary()
#advers.summary()
#advers_full.summary()
#discr_full.summary()
keras.utils.plot_model(discr, to_file=os.path.join(output_folder, "discr_model.pdf"))
keras.utils.plot_model(advers, to_file=os.path.join(output_folder, "advers_model.pdf"))
keras.utils.plot_model(discr_full, to_file=os.path.join(output_folder, "discr_model_full.pdf"))
keras.utils.plot_model(advers_full, to_file=os.path.join(output_folder, "advers_model_full.pdf"))

start_time = timer()
        
if (not load_discr) and train_discr:
    print("Training discriminator")

    batch_size = 5000
    nb_epoch = 50

    history_discr = discr.fit(
            training_features,
            training_targets,
            sample_weight=training_weights,
            batch_size=batch_size,
            epochs=nb_epoch,
            verbose=True,
            validation_data=(testing_features, testing_targets, testing_weights),
            callbacks=callbacks)

    plotTools.draw_keras_history(history_discr, output_folder, 'discr_loss.pdf')
    discr.save_weights(discr_weight_file)

if (not load_advers) and train_advers:
    batch_size = 2048
    nb_epoch = 40

    print("\nTraining adversary!\n")

    scores_train_bkg = discr.predict(training_features[bkg_cut], batch_size=20000)
    scores_test_bkg = discr.predict(testing_features[bkg_cut_test], batch_size=20000)
    
    history_advers = advers.fit(
        scores_train_bkg, 
        training_independent[bkg_cut],
        sample_weight=training_weights[bkg_cut],
        batch_size=batch_size,
        epochs=nb_epoch, 
        verbose=True, 
        validation_data=(scores_test_bkg, testing_independent[bkg_cut_test], testing_weights[bkg_cut_test]))
        #callbacks=[keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=10)])
    
    plotTools.draw_keras_history(history_advers, output_folder, 'advers_loss.pdf')
    advers.save_weights(advers_weight_file)

plotTools.drawPredictedRatio(discr, advers, testing_features, testing_independent, testing_targets, testing_weights, output_folder, 'adversarial_output_pretrained.pdf', only_bkg=True)

if train_pivot:
    batch_size_discr = 32768
    batch_size_advers = 8192
    nb_epoch = 300
    discr_sched = LinearLRScheduler(discr_full, 3e-5, 20, nb_epoch)
    advers_sched = LinearLRScheduler(advers, 5e-4, 2, nb_epoch)

    print("\nTraining full model\n")

    loss_history = {"d": [], "a": [], "f": []}

    for i in range(nb_epoch):
        discr_sched.sched(i)
        advers_sched.sched(i)

        indices = np.random.permutation(len(training_features))[:batch_size_discr]

        loss_full, loss_discr, loss_advers = discr_full.train_on_batch(
                [training_features[indices], training_targets[indices,0]],
                [training_targets[indices,0], training_independent[indices]],
                sample_weight=[training_weights[indices], training_weights[indices]])

        loss_history["f"].append(loss_full)
        loss_history["d"].append(loss_discr)
        loss_history["a"].append(loss_advers)

        scores_train_bkg = discr.predict(training_features[bkg_cut], batch_size=20000)
        
        history_advers = advers.fit(
            scores_train_bkg, 
            training_independent[bkg_cut],
            sample_weight=training_weights[bkg_cut],
            batch_size=batch_size_advers,
            epochs=1, 
            verbose=True) 

        if (not i % 10 and i > 0) or (i+1 == nb_epoch):
            plotTools.drawPredictedRatio(discr, advers, testing_features, testing_independent, testing_targets, testing_weights, output_folder, 'adversarial_output_epoch_{}.pdf'.format(i), only_bkg=True)
        
        plotTools.plotHistories(loss_history, output_folder, "loss_histories.pdf")
        print("Iteration {}/{} -- discr/advers/full model loss: {} / {} / {}".format(i, nb_epoch, loss_discr, loss_advers, loss_full))

    discr.save(output_model_filename)
    export_for_lwtnn(discr, output_model_filename)


end_time = timer()
training_time = datetime.timedelta(seconds=(end_time - start_time))

if do_plots:
    model = keras.models.load_model(output_model_filename)

    draw_non_resonant_training_plots(model, dataset, output_folder, split_by_parameters=add_parameters_columns)

    # Do ROC of SR vs. BR ONLY for background
    bkg_SR_cut = dataset.test_background_extra_dataset[:,0].astype(bool)
    #bkg_SR_cut = (dataset.test_background_extra_dataset >= 75) & (dataset.test_background_extra_dataset < 140)
    #bkg_SR_cut = bkg_SR_cut[:,0]
    scores_bkg = model.predict(dataset.test_background_dataset, batch_size=20000)[:,0]
    score_bkg_SR, _, bins = plotTools.binDataset(scores_bkg[bkg_SR_cut], dataset.test_background_weights[bkg_SR_cut], bins=1000, range=[0,1])
    score_bkg_BR, _, _ = plotTools.binDataset(scores_bkg[~bkg_SR_cut], dataset.test_background_weights[~bkg_SR_cut], bins=bins)
    plotTools.draw_roc(score_bkg_SR, score_bkg_BR, output_dir=output_folder, output_name="roc_SR_vs_BR_bkg.pdf")

    # K-S test for background SR vs. BR
    KS = stats.ks_2samp(scores_bkg[bkg_SR_cut], scores_bkg[~bkg_SR_cut])
    print "K-S test for background, SR vs. BR: TS = {}, p-val = {}".format(*KS)

    #print roc_auc_score(bkg_SR_cut, scores_bkg, sample_weight=dataset.test_background_weights)

    # Do ROC ONLY in SR region
    sig_SR_cut = dataset.test_signal_extra_dataset[:,0].astype(bool)
    #sig_SR_cut = (dataset.test_signal_extra_dataset >= 75) & (dataset.test_signal_extra_dataset < 140)
    #sig_SR_cut = sig_SR_cut[:,0]
    scores_sig = model.predict(dataset.test_signal_dataset[sig_SR_cut], batch_size=20000)[:,0]
    score_sig_SR, _, _ = plotTools.binDataset(scores_sig, dataset.test_signal_weights[sig_SR_cut], bins=bins)
    plotTools.draw_roc(score_sig_SR, score_bkg_SR, output_dir=output_folder, output_name="roc_curve_SR_only.pdf")

    # NN vs. m(jj)
    plotTools.drawNNVersusVar(scores_bkg, dataset.test_background_dataset[:,-1], dataset.test_background_weights, bins=(np.linspace(0, 1, 25), np.linspace(0, 400, 20)), output_dir=output_folder, output_name="nn_vs_mjj_output_bkg.pdf")

print("All done. Training time: %s" % str(training_time))
