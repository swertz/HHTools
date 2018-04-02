import glob
import os
import re
import math
import socket
import json

import array
import numpy as np
import numpy.lib.recfunctions as recfunc

from scipy.optimize import newton
from scipy.stats import norm

from ROOT import TChain, TFile, TTree

from root_numpy import tree2array, rec2array

from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle, safe_indexing

from keras.losses import mean_squared_error, binary_crossentropy
from keras.models import Sequential, Model
from keras.layers import Input, Dense, Dropout, Concatenate
from keras.layers.core import Lambda
from keras.optimizers import Adam, SGD
from keras.regularizers import l2
from keras.layers.normalization import BatchNormalization
from keras.layers.advanced_activations import LeakyReLU

from keras import backend as K
import tensorflow as tf

import plotTools

#INPUT_FOLDER = '/nfs/scratch/fynu/sbrochet/Moriond17/CMSSW_8_0_26_p2_HH_analysis/src/cp3_llbb/HHTools/mvaTraining/inputs/2017-03-02_latest_prod'
INPUT_FOLDER = '/nfs/scratch/fynu/swertz/CMSSW_8_0_25/src/cp3_llbb/HHTools/slurm/170728_skimForTrainingExtra/slurm/output'

HAVE_GPU = 'ingrid-ui8' in socket.gethostname()

def format_nonresonant_parameters(param):
    X_Y =  "{:.2f}_{:.2f}".format(*param).replace(".", "p").replace("-", "m")

    return X_Y

backgrounds = [
        {
            'input': 'TTTo2L2Nu_13TeV-powheg_*_histos.root',
        },

        #{
        #    'input': 'DYJetsToLL_M-10to50_*_histos.root',
        #},

        #{
        #    'input': 'DYToLL_1J_*_histos.root',
        #},

        #{
        #    'input': 'DYToLL_2J_*_histos.root',
        #},

        #{
        #    'input': 'DYToLL_0J_*_histos.root',
        #},

        #{
        #    'input': 'ST_tW_*_5f_*_13TeV-powheg_*_histos.root',
        #},

        ]

resonant_signals = {}
resonant_signal_masses = [260, 270, 300, 350, 400, 450, 500, 550, 600, 650, 750, 800, 900]
for m in resonant_signal_masses:
    resonant_signals[m] = 'GluGluToRadionToHHTo2B2VTo2L2Nu_M-%d_narrow_*_histos.root' % m

# Old grid
# nonresonant_parameters = [(kl, kt) for kl in [-15, -5, -1, 0.0001, 1, 5, 15] for kt in [0.5, 1, 1.75, 2.5]]

# New grid
#nonresonant_parameters = [(kl, kt) for kl in [-20] for kt in [0.5]]
nonresonant_parameters = [(kl, kt) for kl in [-20, -5, 0.0001, 1, 2.4, 3.8, 5, 20] for kt in [0.5, 1, 1.75, 2.5]]

nonresonant_weights = {
            '__base__': "event_weight * trigeff * jjbtag_heavy * jjbtag_light * llidiso * pu",
            # '__base__': "event_weight * trigeff * llidiso * pu",
            'DY.*': "dy_nobtag_to_btagM_weight",
            'GluGluToHHTo2B2VTo2L2Nu': 'sample_weight'
}

resonant_weights = {
            '__base__': "event_weight * trigeff * jjbtag_heavy * jjbtag_light * llidiso * pu",
            # '__base__': "event_weight * trigeff * llidiso * pu",
            'DY.*': "dy_nobtag_to_btagM_weight"
}

# Create map of signal points
nonresonant_signals = {}
for grid_point in nonresonant_parameters:
    X_Y = format_nonresonant_parameters(grid_point)
    nonresonant_signals[grid_point] = 'GluGluToHHTo2B2VTo2L2Nu_point_{}_13TeV-madgraph_*_histos.root'.format(X_Y)


def print_t(t, m=None):
    """
    Print the tensor, shape, min, max, mean, and optional message.
    Use as: tensor = print_t(tensor)
    """
    return tf.Print(t, [t, K.shape(t), K.min(t), K.max(t), K.mean(t)], message=m + ": ")

class LinearLRScheduler:
    def __init__(self, model, lr, factor, nb_epochs):
        """Will apply linear decay of the learning rate, of a factor 'factor' after 'nb_epochs' epochs."""
        self.model = model
        self.lr = lr
        self.factor = factor
        self.nb_epochs = nb_epochs
        K.set_value(model.optimizer.lr, lr)

    def sched(self, epo):
        lr = self.lr * (1 - (1 - 1./self.factor) / self.nb_epochs * epo)
        K.set_value(self.model.optimizer.lr, lr)

def PowerLayer(n):
    """From in input tensor x of shape (None, 1), return a concatenated tensor with [x, x**2, ..., x**n]"""
    def f(x):
        outputs = [x]
        for i in range(2, n + 1):
            outputs.append(K.pow(x, i + 1))
        return K.concatenate(outputs)
    return Lambda(f)


def make_parallel(model, gpu_count):
    """
    Make a Keras model multi-GPU ready
    """

    def get_slice(data, idx, parts):
        shape = tf.shape(data)
        size = tf.concat(0, [ shape[:1] // parts, shape[1:] ])
        stride = tf.concat(0, [ shape[:1] // parts, shape[1:]*0 ])
        start = stride * idx
        return tf.slice(data, start, size)

    outputs_all = []
    for i in range(len(model.outputs)):
        outputs_all.append([])

    #Place a copy of the model on each GPU, each getting a slice of the batch
    for i in range(gpu_count):
        with tf.device('/gpu:%d' % i):
            with tf.name_scope('tower_%d' % i) as scope:

                inputs = []
                #Slice each input into a piece for processing on this GPU
                for x in model.inputs:
                    input_shape = tuple(x.get_shape().as_list())[1:]
                    slice_n = Lambda(get_slice, output_shape=input_shape, arguments={'idx':i,'parts':gpu_count})(x)
                    inputs.append(slice_n)                

                outputs = model(inputs)
                
                if not isinstance(outputs, list):
                    outputs = [outputs]
                
                #Save all the outputs for merging back together later
                for l in range(len(outputs)):
                    outputs_all[l].append(outputs[l])

    # merge outputs on CPU
    with tf.device('/cpu:0'):
        merged = []
        for outputs in outputs_all:
            merged.append(concatenate(outputs, concat_axis=0, name="TEST"))
            
    new_model = Model(input=model.inputs, output=merged)

    funcType = type(model.save)
    # Save the original model instead of multi-GPU compatible one
    def save(self_, filepath, overwrite=True):
        model.save(filepath, overwrite)

    new_model.save = funcType(save, new_model)
    return new_model

def create_resonant_model(n_inputs):
    # Define the model
    model = Sequential()
    model.add(Dense(100, input_dim=n_inputs, activation="relu", kernel_initializer="glorot_uniform"))

    n_hidden_layers = 4
    for i in range(n_hidden_layers):
        model.add(Dense(100, activation="relu", kernel_initializer='glorot_uniform'))
        # if i != (n_hidden_layers - 1):
            # model.add(Dropout(0.1))

    model.add(Dropout(0.2))
    model.add(Dense(1, activation='sigmoid', kernel_initializer='glorot_uniform'))

    # optimizer = Adam(lr=0.000005)
    optimizer = Adam(lr=0.0001)
    model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model

def create_nonresonant_model(n_inputs, n_neurons=100, n_hidden_layers=4, lr=0.0001, dropout=0.35, do_dropout=True, l2_param=0, batch_norm=False, activation="elu", init="he_uniform", multi_gpu=False):

    model = Sequential()
    if batch_norm:
        model.add(BatchNormalization(input_shape=(n_inputs,)))
        model.add(Dense(n_neurons, activation=activation, kernel_initializer=init, kernel_regularizer=l2(l2_param)))
    else:
        model.add(Dense(n_neurons, input_dim=n_inputs, activation=activation, kernel_initializer=init, kernel_regularizer=l2(l2_param)))
    if batch_norm:
        model.add(BatchNormalization())

    for i in range(n_hidden_layers):
        model.add(Dense(n_neurons, activation=activation, kernel_initializer=init, kernel_regularizer=l2(l2_param)))
        if batch_norm:
            model.add(BatchNormalization())

    if do_dropout:
        model.add(Dropout(dropout))
    model.add(Dense(1, activation='sigmoid', kernel_initializer='glorot_uniform'))

    if HAVE_GPU and multi_gpu:
        model = make_parallel(model, 2)

    optimizer = Adam(lr=lr)

    model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model


def create_LSMI_model(n_inputs, n_neurons=100, n_hidden_layers=4, lr=0.01, dropout=0.35, do_dropout=True, l2_param=0, batch_norm=False, activation="elu", init="he_uniform", lamb=1, lsmi_l2=0, sigma_x=1, sigma_y=1):
    def gauss_kernel(x, xp, sigma):
        return tf.exp(-tf.square(x - xp) / (2 * sigma**2))

    def phi_function(x, x_batch, y, y_batch):
        return gauss_kernel(x, x_batch, sigma_x) * gauss_kernel(y, y_batch, sigma_y)

    def LSMI(x, y):
        batch_size = tf.shape(x)[0]
        #x_batch = tf.expand_dims(x, axis=-1)
        #x_rep = tf.tile(tf.transpose(x_batch), tf.shape(x_batch))
        #y_batch = tf.expand_dims(y, axis=-1)
        #y_rep = tf.tile(tf.transpose(y_batch), tf.shape(x_batch))
        #
        #phi_vec = phi_function(x_rep, x_batch, y_rep, y_batch)

        phi_vec = phi_function(x[None,:], x[:,None], y[None,:], y[:,None])

        h_vec = tf.reduce_mean(phi_vec, axis=1)

        #phi_rep = tf.expand_dims(phi_vec, axis=-1)
        #tile_shape = tf.scatter_nd(tf.constant([[2]]), tf.reshape(tf.to_float(batch_size), (1,)), tf.constant([3])) + tf.constant([1, 1, 0], dtype=tf.float32)
        #phi_rep = tf.tile(phi_rep, tf.to_int32(tile_shape))
        #phi_dot = tf.tensordot(phi_rep, tf.transpose(phi_vec), axes=[[2], [0]])
        #norm = tf.to_float(batch_size * batch_size)
        #H_mat = tf.reduce_mean(phi_dot, axis=1) / norm
        phi_vec = phi_function(x[None,:,None], x[:,None,None], y[None,None,:], y[:,None,None]) 
        H_mat = tf.tensordot(phi_vec, phi_vec, axes=([1,2], [1,2])) / tf.to_float(batch_size * batch_size)

        I = lsmi_l2 * tf.eye(batch_size)
        inv = tf.matrix_inverse(H_mat + I)
        h_vec = tf.expand_dims(h_vec, axis=-1)
        theta_vec = tf.tensordot(inv, h_vec, axes=1)

        #lsmi = tf.tensordot(tf.transpose(h_vec), tf.expand_dims(theta_vec, axis=-1), axes=1)
        lsmi = 0.5 * tf.reduce_sum(theta_vec * h_vec) - 0.5

        return lsmi
    
    def lsmi_loss(true, pred):
        true_nn = true[:,0]
        pred_nn = pred[:,0]
        extra = pred[:,1]

        #discr_loss = K.mean(binary_crossentropy(true_nn, pred_nn))
        
        bkg_target = tf.zeros(shape=tf.shape(true_nn))
        bkg_mask = tf.equal(true_nn, bkg_target)
        pred_nn_bkg = tf.boolean_mask(pred_nn, bkg_mask)
        extra_bkg = tf.boolean_mask(extra, bkg_mask)

        lsmi_loss = LSMI(pred_nn_bkg, extra_bkg)
        lsmi_loss = K.reshape(lsmi_loss, (1,1))
        #lsmi_loss = print_t(lsmi_loss, 'lsmi')
        #discr_loss = print_t(discr_loss, 'discr')
        
        return lsmi_loss
        #return discr_loss + lamb * lsmi_loss

    # Define input tensor
    main_input = Input(shape=(n_inputs,))

    # Intermediate tensors for discriminating network
    if batch_norm:
        discr_tensor = BatchNormalization()(main_input)
    else:
        discr_tensor = main_input
    for i in range(1 + n_hidden_layers):
        discr_tensor = Dense(n_neurons, activation=activation, kernel_initializer=init, kernel_regularizer=l2(l2_param))(discr_tensor)
        if batch_norm:
            discr_tensor = BatchNormalization()(discr_tensor)
    if do_dropout:
        discr_tensor = Dropout(dropout)(discr_tensor)
    discr_tensor = Dense(1, activation='sigmoid', kernel_initializer='glorot_uniform')(discr_tensor)
    
    # Training model
    discr_model = Model(inputs=main_input, outputs=discr_tensor)
    optimizer_discr = Adam(lr=lr)
    discr_model.compile(loss='binary_crossentropy', optimizer=optimizer_discr, metrics=['accuracy'])

    # LSMI-loss model
    extra_var_input = Input(shape=(1,))
    if batch_norm:
        extra_var_tensor = BatchNormalization()(extra_var_input)
    else:
        extra_var_tensor = extra_var_input
    lsmi_output = Concatenate()([discr_tensor, extra_var_tensor])
    
    lsmi_model = Model(inputs=[main_input, extra_var_input], outputs=lsmi_output)
    optimizer_lsmi = Adam(lr=lr)
    lsmi_model.compile(loss=lsmi_loss, optimizer=optimizer_lsmi)

    return discr_model, lsmi_model



def create_adversarial_model(n_inputs, n_comp, lamb):

    def make_discr_loss(c):
        def loss(true, pred):
            return c * K.binary_crossentropy(true, pred)
        return loss

    def make_mdn_loss(c):
        def loss(true, params):

            #true = true[:, 0]
            #true = K.expand_dims(true, 1)
            true = K.reshape(true, (-1, 1))
            true = K.repeat_elements(true, n_comp, axis=1)
            
            mu = params[:, :n_comp]
            sigma = params[:, n_comp:2*n_comp] + 10
            pi = params[:, 2*n_comp:]

            #def exponent(mu, true):
            #    return -(true - mu) ** 2 / (2. * sigma ** 2)

            #def gaussian(exponent, sigma, pi):
            #    return pi * ((1. / np.sqrt(2. * np.pi)) / sigma * K.exp(exponent))
            #pdf = K.zeros((n_batch, 1))
            #for i in range(n_comp):
            #    pdf += gaussian(mu[:, i], sigma[:, i], pi[:, i], true)

            exponents = - K.log(pi * ((1. / np.sqrt(2. * np.pi)) / sigma) * (true - mu) ** 2 / (2. * sigma ** 2))
            exponents = K.clip(exponents, -30, 30)
            max_exponent = K.max(exponents, axis=1, keepdims=True)
            max_exponent_repeated = K.repeat_elements(max_exponent, n_comp, axis=1)

            nll = -(max_exponent + K.logsumexp(exponents - max_exponent_repeated, axis=1))

            return c * K.mean(nll)
        return loss

    def make_combined_loss(target):
        def loss(true, pred):
            # Make adversarial loss zero on the signal -- for which target=1
            # We need to keep the batch structure since every entry will be weighted by the event weight
            return (1 - target) * K.binary_crossentropy(true, pred)
        return loss

    def make_trainable(M, trainable=True):
        for l in M.layers:
            l.trainable = trainable
        M.trainable = trainable

    discr_n_nodes = 100
    discr_n_layers = 4
    discr_activation = "relu"
    discr_dropout = 0.3
    discr_batchnorm = True
    discr_l2 = 1e-7
    init = "glorot_uniform"

    # Define input tensor
    main_input = Input(name="discr_input", shape=(n_inputs,))

    # Intermediate tensors for discriminating network

    if discr_batchnorm:
        discr_tensor = BatchNormalization()(main_input)
    else:
        discr_tensor = main_input
    for i in range(1 + discr_n_layers):
        discr_tensor = Dense(discr_n_nodes, activation=discr_activation, kernel_initializer=init, kernel_regularizer=l2(discr_l2))(discr_tensor)
        if discr_batchnorm:
            discr_tensor = BatchNormalization()(discr_tensor)
    if discr_dropout is not None:
        discr_tensor = Dropout(discr_dropout)(discr_tensor)
    discr_tensor = Dense(1, activation='sigmoid', kernel_initializer='glorot_uniform', name='discr_output')(discr_tensor)
    
    # Training model
    discr_model = Model(inputs=main_input, outputs=discr_tensor, name="discr_model")

    # Adversarial network: takes as input the training output
    activation = "selu"
    kernel_init = "he_normal"
    n_power = 3
    n_nodes = 100
    n_layers = 5
    dropout = 0.5
    
    advers_input = Input(shape=(1,), name="advers_input")
    advers_tensor = BatchNormalization()(advers_input)
    if n_power > 0:
        advers_tensor = BatchNormalization()(PowerLayer(n_power)(advers_tensor))
    for i in range(n_layers):
        advers_tensor = BatchNormalization()(Dense(n_nodes, activation=activation, kernel_initializer=kernel_init)(advers_tensor))
    if dropout > 0:
        advers_tensor = Dropout(dropout)(advers_tensor)
    
    # Different outputs for MDN
    #mu = Dense(n_comp, activation="linear", kernel_initializer='glorot_uniform')(advers_tensor)
    #sigma = Dense(n_comp, activation="relu", kernel_initializer='glorot_uniform')(advers_tensor)
    #pi = Dense(n_comp, activation="softmax")(advers_tensor)
    #advers_tensor = concatenate([mu, sigma, pi])
    #advers_tensor = Dense(n_comp, activation="softmax")(advers_tensor)

    # Categorical adversary
    advers_tensor = Dense(n_comp, activation="sigmoid", name="advers_output")(advers_tensor)
    advers_model = Model(inputs=advers_input, outputs=advers_tensor, name="advers_model")
    
    # Adversarial model -- with discriminator nodes
    advers_full_model = Model(inputs=main_input, outputs=advers_model(discr_tensor), name="advers_model_with_discr")

    # "Full" model: combines both networks -- only discriminator trainable
    target_input = Input(shape=(1,))
    discr_full_model = Model(inputs=[main_input, target_input], outputs=[discr_tensor, advers_model(discr_tensor)], name="discr_model with advers")
    
    # First compile discriminating network
    discr_model.compile(loss='binary_crossentropy', optimizer=Adam(lr=2e-5), metrics=['accuracy'])
    
    # Freeze discriminating network, compile adversarial (includes discr.!)
    #make_trainable(advers_full_model, True)
    #make_trainable(discr_model, False)
    #advers_full_model.compile(loss='binary_crossentropy', optimizer=Adam(lr=1e-6))
    #advers_full_model.compile(loss=make_advers_loss(c=1), optimizer=Adam(lr=5e-5))
    advers_model.compile(loss='binary_crossentropy', optimizer=Adam(lr=1e-4))

    # Compile full model with both losses: discriminating is trainable, adversarial is not
    # Careful about the ordere of these calls!
    make_trainable(discr_full_model, False)
    make_trainable(discr_model, True)
    discr_full_model.trainable = True
    discr_full_model.compile(loss=['binary_crossentropy', make_combined_loss(target=target_input)], loss_weights=[1, -lamb], optimizer=Adam(lr=2e-5))

    return discr_model, advers_model, discr_full_model, advers_full_model


def join_expression(*exprs):
    if len(exprs) == 0:
        return ""
    elif len(exprs) == 1:
        return exprs[0]
    else:
        total_expr = "("
        for expr in exprs:
            expr = expr.strip().strip("*")
            if len(expr) == 0:
                continue
            total_expr += "(" + expr + ")*" 
        total_expr = total_expr.strip("*") + ")"
        return total_expr

def skim_arrays(*arrays, **options):
    """
    Randomly select entries from arrays
    """
    rs = np.random.RandomState(42)

    fraction = options.pop('fraction', 1)

    if fraction != 1:
        n_entries = int(math.floor(fraction * len(arrays[0])))

        indices = np.arange(len(arrays[0]))
        rs.shuffle(indices)
        indices = indices[:n_entries]

        return [safe_indexing(a, indices) for a in arrays]

    return arrays

def tree_to_numpy(input_file, variables, weight, cut=None, reweight_to_cross_section=False, n=None):
    """
    Convert a ROOT TTree to a numpy array.
    """

    file_handle = TFile.Open(input_file)

    tree = file_handle.Get('t')

    cross_section = 1
    relative_weight = 1
    if reweight_to_cross_section:
        cross_section = file_handle.Get('cross_section').GetVal()
        relative_weight = cross_section / file_handle.Get("event_weight_sum").GetVal()

    # relative_weight = cross_section / file_handle.Get("event_weight_sum").GetVal()

    if isinstance(weight, dict):
        # Keys are regular expression and values are actual weights. Find the key matching
        # the input filename
        found = False
        weight_expr = None
        if '__base__' in weight:
            weight_expr = weight['__base__']

        for k, v in weight.items():
            if k == '__base__':
                continue

            groups = re.search(k, input_file)
            if not groups:
                continue
            else:
                if found:
                    raise Exception("The input file is matched by more than one weight regular expression. %r" % input_file)

                found = True
                weight_expr = join_expression(weight_expr, v)

        if not weight_expr:
            raise Exception("Not weight expression found for input file %r" % weight_expr)

        weight = weight_expr

    # Read the tree and convert it to a numpy structured array
    a = tree2array(tree, branches=variables + [weight], selection=cut)

    # Rename the last column to 'weight'
    a.dtype.names = variables + ['weight']

    dataset = a[variables]
    weights = a['weight'] * relative_weight

    # Convert to plain numpy arrays
    # dataset = dataset.view((dataset.dtype[0], len(variables))).copy()
    #dataset = np.array(dataset.tolist(), dtype=np.float32)
    dataset = rec2array(dataset)

    if n:
        print("Reading only {} from input tree".format(n))
        dataset = dataset[:n]
        weights = weights[:n]

    return dataset, weights


class DatasetManager:
    def __init__(self, variables, weight_expression, selection, extra_variables=[]):
        """
        Create a new dataset manager

        Parameters:
            variables: list of input variables. This can be either branch names or a more
              complexe mathematical expression
            selection: a cut expression applied to each event. Only events passing this selection are
              kept
            weight_expression: either:
              - a string representing a global weight expression
              - a dict. Keys are regular expression, and values are weight expression. The weight
                  expression chosen will be the one where the keys matches the input file name.
        """

        self.variables = variables
        self.selection = selection
        self.weight_expression = weight_expression
        self.extra_variables = extra_variables

        self.resonant_mass_probabilities = None
        self.nonresonant_parameters_probabilities = None

        self.resonant_masses = None
        self.nonresonant_parameters_list = None
        self.nonresonant_parameters_shift_value = None

    def load_resonant_signal(self, masses=resonant_signal_masses, add_mass_column=False, fraction=1, reweight_to_cross_section=False):
        """
        Load resonant signal

        Parameters:
          masses: list of masses to load
          add_mass_column: if True, a column is added at the end of the dataset with the mass of the sample
          fraction: the fraction of signal events to keep. Default to 1, ie keeping all the events
        """

        self.resonant_masses = masses
        self.n_extra_columns = 1 if add_mass_column else 0

        datasets = []
        weights = []
        p = [[], []]

        print("Loading resonant signal...")

        for m in masses:
            f = get_file_from_glob(os.path.join(INPUT_FOLDER, resonant_signals[m]))
            dataset, weight = tree_to_numpy(f, self.variables + self.extra_variables, self.weight_expression, self.selection, reweight_to_cross_section=reweight_to_cross_section)

            if fraction != 1:
                dataset, weight = skim_arrays(dataset, weight, fraction=fraction)

            p[0].append(m)
            p[1].append(len(dataset))

            if add_mass_column:
                # FIXME -- if parameterised, convert to plain numpy array,
                # otherwise keep it as a structured array
                mass_col = np.empty(len(dataset)) # dtype=[('resonant_mass', '<f4')])
                mass_col.fill(m)
                dataset = np.c_[dataset, mass_col]

            datasets.append(dataset)
            weights.append(weight)

        # Normalize probabilities in order that sum(p) = 1
        p[1] = np.array(p[1], dtype='float')
        p[1] /= np.sum(p[1])

        self.signal_dataset = np.concatenate(datasets)
        self.signal_weights = np.concatenate(weights)
        self.resonant_mass_probabilities = p

        print("Done. Number of signal events: %d ; Sum of weights: %.4f" % (len(self.signal_dataset), np.sum(self.signal_weights)))

    def load_nonresonant_signal(self, parameters_list=nonresonant_parameters, add_parameters_columns=False, fraction=1, parameters_shift=None, reweight_to_cross_section=False):

        self.nonresonant_parameters_list = self._user_to_positive_parameters_list(parameters_list, parameters_shift)

        self.n_extra_columns = 2 if add_parameters_columns else 0

        datasets = []
        weights = []
        p = [[], []]

        print("Loading nonresonant signal...")

        for i, parameters in enumerate(parameters_list):
            print("For parameters: {}".format(parameters))
            files = get_files_from_glob(os.path.join(INPUT_FOLDER, nonresonant_signals[parameters]))

            dataset = []
            weight = []
            for f in files:
                dataset_, weight_ = tree_to_numpy(f, self.variables + self.extra_variables, self.weight_expression, self.selection, reweight_to_cross_section=reweight_to_cross_section)
                weight.append(weight_)
                dataset.append(dataset_)

            dataset = np.concatenate(dataset)
            weight = np.concatenate(weight)

            if fraction != 1:
                dataset, weight = skim_arrays(dataset, weight, fraction=fraction)

            p[0].append(self.nonresonant_parameters_list[i])
            p[1].append(np.sum(weight))

            if add_parameters_columns:
                for parameter in self.nonresonant_parameters_list[i]:
                    col = np.empty(len(dataset))
                    col.fill(parameter)
                    dataset = np.c_[dataset, col]

            datasets.append(dataset)
            weights.append(weight)

        # Normalize probabilities in order that sum(p) = 1
        p[1] = np.array(p[1], dtype='float')
        p[1] /= np.sum(p[1])

        self.signal_dataset = np.concatenate(datasets)
        self.signal_weights = np.concatenate(weights)
        self.nonresonant_parameters_probabilities = p

        print("Done. Number of signal events: %d ; Sum of weights: %.10f" % (len(self.signal_dataset), np.sum(self.signal_weights)))

    def load_backgrounds(self, add_mass_column=False, add_parameters_columns=False):

        if add_mass_column and add_parameters_columns:
            raise Exception("add_mass_column and add_parameters_columns are mutually exclusive")

        if add_mass_column and not self.resonant_mass_probabilities:
            raise Exception("You need to first load the resonant signal before the background")

        if add_parameters_columns and not self.nonresonant_parameters_probabilities:
            raise Exception("You need to first load the nonresonant signals before the background")

        datasets = []
        weights = []

        print("Loading backgrounds...")

        for background in backgrounds:
            files = get_files_from_glob(os.path.join(INPUT_FOLDER, background['input']))

            dataset = []
            weight = []
            for f in files:
                print("  {}...".format(os.path.basename(f)))
                dataset_, weight_ = tree_to_numpy(f, self.variables + self.extra_variables, self.weight_expression, self.selection, reweight_to_cross_section=True)
                weight.append(weight_)
                dataset.append(dataset_)

            dataset = np.concatenate(dataset)
            weight = np.concatenate(weight)

            probabilities = None
            if add_mass_column:
                probabilities = self.resonant_mass_probabilities
            elif add_parameters_columns:
                probabilities = self.nonresonant_parameters_probabilities

            if probabilities:
                rs = np.random.RandomState(42)

                indices = rs.choice(len(probabilities[0]), len(dataset), p=probabilities[1])
                cols = np.array(np.take(probabilities[0], indices, axis=0), dtype='float')
                dataset = np.c_[dataset, cols]

            datasets.append(dataset)
            weights.append(weight)

        self.background_dataset = np.concatenate(datasets)
        self.background_weights = np.concatenate(weights)

        print("Done. Number of background events: %d ; Sum of weights: %.4f" % (len(self.background_dataset), np.sum(self.background_weights)))

    def update_background_mass_column(self):
        rs = np.random.RandomState(42)
        mass_col = np.array(rs.choice(self.resonant_mass_probabilities[0], len(self.background_dataset), p=self.resonant_mass_probabilities[1]), dtype='float')

        self.background_dataset[:, len(self.variables)] = mass_col

    def update_background_parameters_column(self):
        rs = np.random.RandomState(42)
        probabilities = self.nonresonant_parameters_probabilities

        indices = rs.choice(len(probabilities[0]), len(self.background_dataset), p=probabilities[1])
        cols = np.array(np.take(probabilities[0], indices, axis=0), dtype='float')

        for i in range(cols.shape[1]):
            self.background_dataset[:, len(self.variables) + i] = cols[:, i]

    def split(self, reweight_signal_training_sample=True, reweight_signal_testing_sample=False, test_size=0.5):
        """
        Split datasets into a training and testing samples

        Parameter:
            reweight_signal_training_sample: If true, the signal training sample is reweighted so that the sum of weights of signal and background are the same
            reweight_signal_testing_sample: If true, the signal testing sample is reweighted so that the sum of weights of signal and background are the same
        """

        self.train_signal_dataset, self.test_signal_dataset, self.train_signal_weights, self.test_signal_weights = train_test_split(self.signal_dataset, self.signal_weights, test_size=test_size, random_state=42)
        self.train_background_dataset, self.test_background_dataset, self.train_background_weights, self.test_background_weights = train_test_split(self.background_dataset, self.background_weights, test_size=test_size, random_state=42)

        if reweight_signal_training_sample:
            sumw_train_signal = np.sum(self.train_signal_weights)
            sumw_train_background = np.sum(self.train_background_weights)

            ratio = sumw_train_background / sumw_train_signal
            self.train_signal_weights *= ratio
            print("Signal training sample reweighted so that sum of event weights for signal and background match. Sum of event weight = %.4f" % (np.sum(self.train_signal_weights)))

        if reweight_signal_testing_sample:
            sumw_test_signal = np.sum(self.test_signal_weights)
            sumw_test_background = np.sum(self.test_background_weights)

            ratio = sumw_test_background / sumw_test_signal
            self.test_signal_weights *= ratio
            print("Signal testing sample reweighted so that sum of event weights for signal and background match. Sum of event weight = %.4f" % (np.sum(self.test_signal_weights)))

        # Create merged training and testing dataset, with targets
        self.training_dataset = np.vstack((self.train_signal_dataset, self.train_background_dataset))
        self.training_weights = np.hstack((self.train_signal_weights, self.train_background_weights))
        self.testing_dataset = np.vstack((self.test_signal_dataset, self.test_background_dataset))
        self.testing_weights = np.hstack((self.test_signal_weights, self.test_background_weights))

        # Create target variable (1 for signal, 0 for background)
        #self.training_targets = np.concatenate(np.array([1] * len(self.train_signal_dataset) + [0] * len(self.train_background_dataset)).reshape((-1,1))
        #self.testing_targets = np.array([1] * len(self.test_signal_dataset) + [0] * len(self.test_background_dataset)).reshape((-1,1))
        self.training_targets = np.vstack((
                np.ones((self.train_signal_dataset.shape[0], 1)), 
                np.zeros((self.train_background_dataset.shape[0], 1))
            ))
        self.testing_targets = np.vstack((
                np.ones((self.test_signal_dataset.shape[0], 1)), 
                np.zeros((self.test_background_dataset.shape[0], 1))
            ))

        # Shuffle everything
        self.training_dataset, self.training_weights, self.training_targets = shuffle(self.training_dataset, self.training_weights, self.training_targets, random_state=42)
        self.testing_dataset, self.testing_weights, self.testing_targets = shuffle(self.testing_dataset, self.testing_weights, self.testing_targets, random_state=42)

        def to_array(a):
            return a.view( (np.float32, len(a.dtype.names)) )

        # We've been working with structured arrays
        # => use regular arrays, and split between variables and extra variables

        self.training_extra_dataset         = self.training_dataset[:,len(self.variables):]
        self.training_dataset               = self.training_dataset[:,:len(self.variables)]
        
        self.testing_extra_dataset          = self.testing_dataset[:,len(self.variables):]
        self.testing_dataset                = self.testing_dataset[:,:len(self.variables)]

        self.train_signal_extra_dataset     = self.train_signal_dataset[:,len(self.variables):]
        self.train_signal_dataset           = self.train_signal_dataset[:,:len(self.variables)]
        
        self.test_signal_extra_dataset      = self.test_signal_dataset[:,len(self.variables):]
        self.test_signal_dataset            = self.test_signal_dataset[:,:len(self.variables)]

        self.train_background_extra_dataset = self.train_background_dataset[:,len(self.variables):]
        self.train_background_dataset       = self.train_background_dataset[:,:len(self.variables)]

        self.test_background_extra_dataset  = self.test_background_dataset[:,len(self.variables):]
        self.test_background_dataset        = self.test_background_dataset[:,:len(self.variables)]

    def normalise_training_weights(self):
        """Normalise training weights s.t. sum(sig&bkg weights) = number of sig&bkg events"""
        ratio = len(self.training_weights) / np.sum(self.training_weights)
        self.training_weights *= ratio
        self.train_signal_weights *= ratio
        self.train_background_weights *= ratio

    def normalise_testing_weights(self):
        """Normalise testing weights s.t. sum(sig&bkg weights) = number of sig&bkg events"""
        ratio = len(self.testing_weights) / np.sum(self.testing_weights)
        self.testing_weights *= ratio
        self.test_signal_weights *= ratio
        self.test_background_weights *= ratio
        
    def get_training_datasets(self):
        return self.train_signal_dataset, self.train_background_dataset

    def get_testing_datasets(self):
        return self.test_signal_dataset, self.test_background_dataset

    def get_training_weights(self):
        return self.train_signal_weights, self.train_background_weights

    def get_testing_weights(self):
        return self.test_signal_weights, self.test_background_weights

    def get_training_combined_dataset_and_targets(self):
        return self.training_dataset, self.training_targets

    def get_testing_combined_dataset_and_targets(self):
        return self.testing_dataset, self.testing_targets

    def get_training_combined_weights(self):
        return self.training_weights

    def get_testing_combined_weights(self):
        return self.testing_weights

    def get_training_testing_signal_predictions(self, model, **kwargs):
        return self._get_predictions(model, self.train_signal_dataset, **kwargs), self._get_predictions(model, self.test_signal_dataset, **kwargs)

    def get_signal_predictions(self, model, **kwargs):
        return self._get_predictions(model, self.signal_dataset, **kwargs)

    def get_signal_weights(self):
        return self.signal_weights

    def get_training_testing_background_predictions(self, model, **kwargs):
        return self._get_predictions(model, self.train_background_dataset, **kwargs), self._get_predictions(model, self.test_background_dataset, **kwargs)

    def get_background_predictions(self, model, **kwargs):
        return self._get_predictions(model, self.background_dataset, **kwargs)

    def get_background_weights(self):
        return self.background_weights

    def _get_predictions(self, model, values, **kwargs):
        return model.predict(values, batch_size=20000)[:,0]

    def draw_inputs(self, output_dir):

        print("Plotting input variables...")
        variables = self.variables[:]

        if self.n_extra_columns > 0:
            if self.resonant_masses:
                variables += ['mass_hypothesis']
            elif self.nonresonant_parameters_list:
                variables += ['k_l', 'k_t']

        for index, variable in enumerate(variables):
            output_file = os.path.join(output_dir, variable + ".pdf") 
            plotTools.drawTrainingTestingComparison(
                    training_background_data=self.train_background_dataset[:, index],
                    training_signal_data=self.train_signal_dataset[:, index],
                    testing_background_data=self.test_background_dataset[:, index],
                    testing_signal_data=self.test_signal_dataset[:, index],

                    training_background_weights=self.train_background_weights,
                    training_signal_weights=self.train_signal_weights,
                    testing_background_weights=self.test_background_weights,
                    testing_signal_weights=self.test_signal_weights,

                    x_label=variable,
                    output=output_file
                    )

        print("Done.")

    def compute_shift_values(self, parameters_list):
        shift = [abs(min(x)) if min(x) < 0 else 0 for x in zip(*parameters_list)]
        print("Shifting all non-resonant parameters by {}".format(shift))

        return shift

    def _user_to_positive_parameters_list(self, parameters_list, parameters_shift=None):
        if not parameters_shift:
            self.nonresonant_parameters_shift_value = self.compute_shift_values(parameters_list)
        else:
            self.nonresonant_parameters_shift_value = parameters_shift[:]

        shifted_parameters_list = parameters_list[:]
        for i in range(len(parameters_list)):
            shifted_parameters_list[i] = tuple([x + self.nonresonant_parameters_shift_value[j] for j, x in enumerate(parameters_list[i])])

        return shifted_parameters_list

    def _positive_to_user_parameters_list(self, parameters_list):
        if not self.nonresonant_parameters_shift_value:
            raise Exception('Cannot invert parameters transformation since _user_to_positive_parameters was not called')

        shifted_parameters_list = parameters_list[:]
        for i in range(len(parameters_list)):
            shifted_parameters_list[i] = tuple([x - self.nonresonant_parameters_shift_value[j] for j, x in enumerate(parameters_list[i])])

        return shifted_parameters_list

    def positive_to_user_parameters(self, parameters):
        if not self.nonresonant_parameters_shift_value:
            raise Exception('Cannot invert parameters transformation since _user_to_positive_parameters was not called')

        return tuple([x - self.nonresonant_parameters_shift_value[j] for j, x in enumerate(parameters)])

    def get_nonresonant_parameters_list(self):
        return self.nonresonant_parameters_list
        # return self._positive_to_user_parameters_list(self.nonresonant_parameters_list)

def get_file_from_glob(f):
    files = glob.glob(f)
    if len(files) != 1:
        raise Exception('Only one input file is supported per glob pattern: %s -> %s' % (f, files))

    return files[0]

def get_files_from_glob(f):
    files = glob.glob(f)
    if len(files) == 0:
        raise Exception('No file matching glob pattern: %s' % f)

    return files

def draw_nn_vs_independent(model, dataset, bins, output_folder):
    
    testing_features = dataset.test_background_dataset
    testing_independent = dataset.test_background_extra_dataset.ravel()
    testing_weights = dataset.test_background_weights

    _, testing_background_predictions = dataset.get_training_testing_background_predictions(model)

    plotTools.drawNNVersusVar(testing_background_predictions, testing_independent, testing_weights, bins=(np.linspace(0, 1, 25), bins), output_dir=output_folder, output_name="nn_vs_mjj_output_bkg.pdf")

def draw_non_resonant_training_plots(model, dataset, output_folder, split_by_parameters=False):

    #plot(model, to_file=os.path.join(output_folder, "model.pdf"))

    # Draw inputs
    output_input_plots = os.path.join(output_folder, 'inputs')
    if not os.path.exists(output_input_plots):
        os.makedirs(output_input_plots)

    dataset.draw_inputs(output_input_plots)

    training_dataset, training_targets = dataset.get_training_combined_dataset_and_targets()
    training_weights = dataset.get_training_combined_weights()

    testing_dataset, testing_targets = dataset.get_testing_combined_dataset_and_targets()
    testing_weights = dataset.get_testing_combined_weights()

    print("Evaluating model performances...")

    training_signal_weights, training_background_weights = dataset.get_training_weights()
    testing_signal_weights, testing_background_weights = dataset.get_testing_weights()

    training_signal_predictions, testing_signal_predictions = dataset.get_training_testing_signal_predictions(model)
    training_background_predictions, testing_background_predictions = dataset.get_training_testing_background_predictions(model)

    print("Done.")

    print("Plotting time...")

    ## NN output
    plotTools.drawNNOutput(training_background_predictions, testing_background_predictions,
            training_signal_predictions, testing_signal_predictions,
            training_background_weights, testing_background_weights,
            training_signal_weights, testing_signal_weights,
            output_dir=output_folder, output_name="nn_output.pdf", bins=50, 

            #testing_signal_indices=[ (dataset.test_signal_extra_dataset[:,0] > 75) & (dataset.test_signal_extra_dataset[:,0] <= 140), ~((dataset.test_signal_extra_dataset[:,0] > 75) & (dataset.test_signal_extra_dataset[:,0] <= 140))],
            #testing_background_indices=[ (dataset.test_background_extra_dataset[:,0] > 75) & (dataset.test_background_extra_dataset[:,0] <= 140), ~((dataset.test_background_extra_dataset[:,0] > 75) & (dataset.test_background_extra_dataset[:,0] <= 140)) ],
            testing_signal_indices=[ dataset.test_signal_extra_dataset[:,0].astype(bool), ~(dataset.test_signal_extra_dataset[:,0].astype(bool)) ],
            testing_background_indices=[ dataset.test_background_extra_dataset[:,0].astype(bool), ~(dataset.test_background_extra_dataset[:,0].astype(bool)) ],
            indices_ranges=["SR", "BR"]
            #testing_signal_indices=[ dataset.test_signal_extra_dataset <= 75, (dataset.test_signal_extra_dataset > 75) & (dataset.test_signal_extra_dataset <= 140), dataset.test_signal_extra_dataset > 140 ],
            #testing_background_indices=[ dataset.test_background_extra_dataset <= 75, (dataset.test_background_extra_dataset > 75) & (dataset.test_background_extra_dataset <= 140), dataset.test_background_extra_dataset > 140 ],
            #indices_ranges=["mjj < 75", "75 < mjj < 140", "mjj > 140"]
            )

    # ROC curve
    binned_training_background_predictions, _, bins = plotTools.binDataset(training_background_predictions, training_background_weights, bins=1000, range=[0, 1])
    binned_training_signal_predictions, _, _ = plotTools.binDataset(training_signal_predictions, training_signal_weights, bins=bins)
    plotTools.draw_roc(binned_training_signal_predictions, binned_training_background_predictions, output_dir=output_folder, output_name="roc_curve.pdf")

    if split_by_parameters:
        output_folder = os.path.join(output_folder, 'splitted_by_parameters')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        training_signal_dataset, training_background_dataset = dataset.get_training_datasets()
        testing_signal_dataset, testing_background_dataset = dataset.get_testing_datasets()
        for parameters in dataset.get_nonresonant_parameters_list():
            user_parameters = ['{:.2f}'.format(x) for x in dataset.positive_to_user_parameters(parameters)]

            print("  Plotting NN output and ROC curve for %s" % str(user_parameters))

            training_signal_mask = (training_signal_dataset[:,-1] == parameters[1]) & (training_signal_dataset[:,-2] == parameters[0])
            training_background_mask = (training_background_dataset[:,-1] == parameters[1]) & (training_background_dataset[:,-2] == parameters[0])
            testing_signal_mask = (testing_signal_dataset[:,-1] == parameters[1]) & (testing_signal_dataset[:,-2] == parameters[0])
            testing_background_mask = (testing_background_dataset[:,-1] == parameters[1]) & (testing_background_dataset[:,-2] == parameters[0])

            p_training_background_predictions = training_background_predictions[training_background_mask]
            p_testing_background_predictions = testing_background_predictions[testing_background_mask]
            p_training_signal_predictions = training_signal_predictions[training_signal_mask]
            p_testing_signal_predictions = testing_signal_predictions[testing_signal_mask]

            p_training_background_weights = training_background_weights[training_background_mask]
            p_testing_background_weights = testing_background_weights[testing_background_mask]
            p_training_signal_weights = training_signal_weights[training_signal_mask]
            p_testing_signal_weights = testing_signal_weights[testing_signal_mask]

            suffix = format_nonresonant_parameters(user_parameters)
            plotTools.drawNNOutput(
                         p_training_background_predictions, p_testing_background_predictions,
                         p_training_signal_predictions, p_testing_signal_predictions,
                         p_training_background_weights, p_testing_background_weights,
                         p_training_signal_weights, p_testing_signal_weights,
                         output_dir=output_folder, output_name="nn_output_fixed_parameters_%s.pdf" % (suffix), bins=50)

            binned_training_background_predictions, _, bins = plotTools.binDataset(p_training_background_predictions, p_training_background_weights, bins=50, range=[0, 1])
            binned_training_signal_predictions, _, _ = plotTools.binDataset(p_training_signal_predictions, p_training_signal_weights, bins=bins)
            plotTools.draw_roc(binned_training_signal_predictions, binned_training_background_predictions, output_dir=output_folder, output_name="roc_curve_fixed_parameters_%s.pdf" % (suffix))
    print("Done")

def draw_resonant_training_plots(model, dataset, output_folder, split_by_mass=False):

    # plot(model, to_file=os.path.join(output_folder, "model.pdf"))

    # Draw inputs
    output_input_plots = os.path.join(output_folder, 'inputs')
    if not os.path.exists(output_input_plots):
        os.makedirs(output_input_plots)

    dataset.draw_inputs(output_input_plots)

    training_dataset, training_targets = dataset.get_training_combined_dataset_and_targets()
    training_weights = dataset.get_training_combined_weights()

    testing_dataset, testing_targets = dataset.get_testing_combined_dataset_and_targets()
    testing_weights = dataset.get_testing_combined_weights()

    print("Evaluating model performances...")

    training_signal_weights, training_background_weights = dataset.get_training_weights()
    testing_signal_weights, testing_background_weights = dataset.get_testing_weights()

    training_signal_predictions, testing_signal_predictions = dataset.get_training_testing_signal_predictions(model)
    training_background_predictions, testing_background_predictions = dataset.get_training_testing_background_predictions(model)

    print("Done.")

    print("Plotting time...")

    # NN output
    plotTools.drawNNOutput(training_background_predictions, testing_background_predictions,
                 training_signal_predictions, testing_signal_predictions,
                 training_background_weights, testing_background_weights,
                 training_signal_weights, testing_signal_weights,
                 output_dir=output_folder, output_name="nn_output.pdf", bins=50)

    # ROC curve
    binned_training_background_predictions, _, bins = plotTools.binDataset(training_background_predictions, training_background_weights, bins=50, range=[0, 1])
    binned_training_signal_predictions, _, _ = plotTools.binDataset(training_signal_predictions, training_signal_weights, bins=bins)
    plotTools.draw_roc(binned_training_signal_predictions, binned_training_background_predictions, output_dir=output_folder, output_name="roc_curve.pdf")

    if split_by_mass:
        output_folder = os.path.join(output_folder, 'splitted_by_mass')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        training_signal_dataset, training_background_dataset = dataset.get_training_datasets()
        testing_signal_dataset, testing_background_dataset = dataset.get_testing_datasets()
        for m in dataset.resonant_masses:
            print("  Plotting NN output and ROC curve for M=%d" % m)

            training_signal_mask = training_signal_dataset[:,-1] == m
            training_background_mask = training_background_dataset[:,-1] == m
            testing_signal_mask = testing_signal_dataset[:,-1] == m
            testing_background_mask = testing_background_dataset[:,-1] == m

            p_training_background_predictions = training_background_predictions[training_background_mask]
            p_testing_background_predictions = testing_background_predictions[testing_background_mask]
            p_training_signal_predictions = training_signal_predictions[training_signal_mask]
            p_testing_signal_predictions = testing_signal_predictions[testing_signal_mask]

            p_training_background_weights = training_background_weights[training_background_mask]
            p_testing_background_weights = testing_background_weights[testing_background_mask]
            p_training_signal_weights = training_signal_weights[training_signal_mask]
            p_testing_signal_weights = testing_signal_weights[testing_signal_mask]

            plotTools.drawNNOutput(
                         p_training_background_predictions, p_testing_background_predictions,
                         p_training_signal_predictions, p_testing_signal_predictions,
                         p_training_background_weights, p_testing_background_weights,
                         p_training_signal_weights, p_testing_signal_weights,
                         output_dir=output_folder, output_name="nn_output_fixed_M%d.pdf" % (m),
                         bins=50)

            binned_training_background_predictions, _, bins = plotTools.binDataset(p_training_background_predictions, p_training_background_weights, bins=50, range=[0, 1])
            binned_training_signal_predictions, _, _ = plotTools.binDataset(p_training_signal_predictions, p_training_signal_weights, bins=bins)
            plotTools.draw_roc(binned_training_signal_predictions, binned_training_background_predictions, output_dir=output_folder, output_name="roc_curve_fixed_M_%d.pdf" % (m))
    print("Done")

def save_training_parameters(output, model, **kwargs):
    parameters = {
            'extra': kwargs
            }

    model_definition = model.to_json()
    m = json.loads(model_definition)
    parameters['model'] = m

    with open(os.path.join(output, 'parameters.json'), 'w') as f:
        json.dump(parameters, f, indent=4)


def export_for_lwtnn(model, name):
    base, _ = os.path.splitext(name)

    # Export architecture of the model
    with open(base + '_arch.json', 'w') as f:
        f.write(model.to_json())

    # And the weights
    model.save_weights(base + "_weights.h5")


def get_median_expected_limit(sig_binned, bkg_binned, guess=10):
    def median_function(s, b):
        def f(mu):
            return np.sqrt(- 2 * (np.sum(b * np.log(1 + mu * s/b) - mu * s))) - norm.ppf(0.95)
        return f

    if np.sum(bkg_binned <= 0) != 0:
        print("Warning: b has invalid bins!")
        return None
    
    try:
        limit = newton(median_function(sig_binned[0], bkg_binned[0]), guess)
    except RuntimeError:
        print("Warning: could not compute limit!")
        return None

    return limit
