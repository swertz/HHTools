import glob
import os

import array
import numpy as np
import numpy.lib.recfunctions as recfunc

from ROOT import TChain, TFile, TTree

from root_numpy import tree2array

from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

from keras.models import Sequential
from keras.layers import Dense, Dropout

INPUT_FOLDER = '/home/fynu/sbrochet/scratch/Framework/CMSSW_8_0_24_patch1_HH_Analysis/src/cp3_llbb/HHTools/histFactory_hh/2016-12-13_trees_with_dy_estimate_for_mva_training_and_issf/condor/output'

backgrounds = [
        {
            'input': 'TTTo2L2Nu_13TeV-powheg_*_histos.root',
        },

        {
            'input': 'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_*_histos.root',
        },

        {
            'input': 'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_*_histos.root',
        },

        # {
            # 'inputs': ['ST_tW_top_5f_inclusiveDecays_13TeV-powheg_*_histos.root'],
        # },

        # {
            # 'inputs': ['ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg_*_histos.root'],
        # },
        
        ]

resonant_signals = {}
resonant_signal_masses = [400, 650, 900]
for m in resonant_signal_masses:
    resonant_signals[m] = 'GluGluToRadionToHHTo2B2VTo2L2Nu_M-%d_narrow_Spring16MiniAODv2_*_histos.root' % m

def create_resonant_model(n_inputs):
    # Define the model
    model = Sequential()
    model.add(Dense(100, input_dim=n_inputs, activation="relu", init="glorot_uniform"))
    model.add(Dense(100, activation="relu", init='glorot_uniform'))
    model.add(Dense(100, activation="relu", init='glorot_uniform'))
    model.add(Dropout(0.1))
    model.add(Dense(2, activation='softmax', init='glorot_uniform'))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    model.summary()

    return model

def tree_to_numpy(input_file, variables, weight, cut=None, reweight_to_cross_section=False):
    file_handle = TFile.Open(input_file)

    tree = file_handle.Get('t')

    cross_section = 1
    relative_weight = 1
    if reweight_to_cross_section:
        cross_section = file_handle.Get('cross_section').GetVal()
        relative_weight = cross_section / file_handle.Get("event_weight_sum").GetVal()

    # relative_weight = cross_section / file_handle.Get("event_weight_sum").GetVal()

    # Read the tree and convert it to a numpy structured array
    a = tree2array(tree, branches=variables + [weight], selection=cut)

    # Rename the last column to 'weight'
    a.dtype.names = variables + ['weight']

    dataset = a[variables]
    weights = a['weight'] * relative_weight

    # Convert to plain numpy arrays
    # dataset = dataset.view((dataset.dtype[0], len(variables))).copy()
    dataset = np.array(dataset.tolist(), dtype=np.float32)

    return dataset, weights


class DatasetManager:
    def __init__(self, variables, weight_expression, selection):
        self.variables = variables
        self.weight_expression = weight_expression
        self.selection = selection

        self.resonant_mass_probabilities = None

    def load_resonant_signal(self, masses=resonant_signal_masses, add_mass_column=False):
        datasets = []
        weights = []
        p = [[], []]

        print("Loading resonant signal...")

        for m in masses:
            f = get_file_from_glob(os.path.join(INPUT_FOLDER, resonant_signals[m]))
            dataset, weight = tree_to_numpy(f, self.variables, self.weight_expression, self.selection, reweight_to_cross_section=False)
            weights.append(weight)

            p[0].append(m)
            p[1].append(len(dataset))

            if add_mass_column:
                mass_col = np.empty(len(dataset)) # dtype=[('resonant_mass', '<f4')])
                mass_col.fill(m)
                dataset = np.c_[dataset, mass_col]

            datasets.append(dataset)

        # Normalize probabilities in order that sum(p) = 1
        p[1] = np.array(p[1], dtype='float')
        p[1] /= np.sum(p[1])

        self.signal_dataset = np.concatenate(datasets)
        self.signal_weights = np.concatenate(weights)
        self.resonant_mass_probabilities = p

        print("Done. Number of signal events: %d ; Sum of weights: %.4f" % (len(self.signal_dataset), np.sum(self.signal_weights)))

    def load_backgrounds(self, add_mass_column=False):

        if add_mass_column and not self.resonant_mass_probabilities:
            raise Exception("You need to first load the resonant signal before the background")

        datasets = []
        weights = []

        print("Loading backgrounds...")

        for background in backgrounds:
            f = get_file_from_glob(os.path.join(INPUT_FOLDER, background['input']))
            dataset, weight = tree_to_numpy(f, self.variables, self.weight_expression, self.selection, reweight_to_cross_section=True)
            weights.append(weight)

            if add_mass_column:
                rs = np.random.RandomState(42)
                mass_col = np.array(rs.choice(self.resonant_mass_probabilities[0], len(dataset), p=self.resonant_mass_probabilities[1]), dtype='float')
                dataset = np.c_[dataset, mass_col]

            datasets.append(dataset)

        self.background_dataset = np.concatenate(datasets)
        self.background_weights = np.concatenate(weights)

        print("Done. Number of background events: %d ; Sum of weights: %.4f" % (len(self.background_dataset), np.sum(self.background_weights)))


    def split(self, reweight_background_training_sample=True):
        """
        Split datasets into a training and testing samples

        Parameter:
            reweight_background_training_sample: If true, the background training sample is reweighted so that the sum of weights of signal and background are the same
        """

        self.train_signal_dataset, self.test_signal_dataset, self.train_signal_weights, self.test_signal_weights = train_test_split(self.signal_dataset, self.signal_weights, test_size=0.5, random_state=42)
        self.train_background_dataset, self.test_background_dataset, self.train_background_weights, self.test_background_weights = train_test_split(self.background_dataset, self.background_weights, test_size=0.5, random_state=42)

        if reweight_background_training_sample:
            sumw_train_signal = np.sum(self.train_signal_weights)
            sumw_train_background = np.sum(self.train_background_weights)

            ratio = sumw_train_signal / sumw_train_background
            self.train_background_weights *= ratio
            print("Background training sample reweighted so that sum of event weights for signal and background match. Sum of event weight = %.4f" % (np.sum(self.train_signal_weights)))

        # Create merged training and testing dataset, with targets
        self.training_dataset = np.concatenate([self.train_signal_dataset, self.train_background_dataset])
        self.training_weights = np.concatenate([self.train_signal_weights, self.train_background_weights])
        self.testing_dataset = np.concatenate([self.train_signal_dataset, self.train_background_dataset])
        self.testing_weights = np.concatenate([self.train_signal_weights, self.train_background_weights])

        # Create one-hot vector, the target of the training
        # A hot-vector is a N dimensional vector, where N is the number of classes
        # Here we assume that class 0 is signal, and class 1 is background
        # So we have [1 0] for signal and [0 1] for background
        self.training_targets = np.array([[1, 0]] * len(self.train_signal_dataset) + [[0, 1]] * len(self.train_background_dataset))
        self.testing_targets = np.array([[1, 0]] * len(self.train_signal_dataset) + [[0, 1]] * len(self.train_background_dataset))

        # Shuffle everything
        self.training_dataset, self.training_weights, self.training_targets = shuffle(self.training_dataset, self.training_weights, self.training_targets, random_state=42)
        self.testing_dataset, self.testing_weights, self.testing_targets = shuffle(self.testing_dataset, self.testing_weights, self.testing_targets, random_state=42)

    def get_training_datasets(self):
        return self.train_signal_dataset, self.train_background_dataset

    def get_testing_datasets(self):
        return self.train_signal_dataset, self.train_background_dataset

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

    def get_training_testing_signal_predictions(self, model):
        return self._get_predictions(model, self.train_signal_dataset), self._get_predictions(model, self.test_signal_dataset)

    def get_signal_predictions(self, model):
        return self._get_predictions(model, self.signal_dataset)

    def get_signal_weights(self):
        return self.signal_weights

    def get_training_testing_background_predictions(self, model):
        return self._get_predictions(model, self.train_background_dataset), self._get_predictions(model, self.test_background_dataset)

    def get_background_predictions(self, model):
        return self._get_predictions(model, self.background_dataset)

    def get_background_weights(self):
        return self.background_weights

    def _get_predictions(self, model, values):
        predictions = model.predict(values)
        return np.delete(predictions, 1, axis=1).flatten()

def get_file_from_glob(f):
    files = glob.glob(f)
    if len(files) != 1:
        raise Exception('Only one input file is supported per glob pattern: %s' % files)

    return files[0]
