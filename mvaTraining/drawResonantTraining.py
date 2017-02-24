import glob
import os
import pickle
import gzip
import datetime
import argparse

import plotTools

from common import *

import keras

parser = argparse.ArgumentParser(description='Plot NN output and ROC curve of a training for various resonant masses.')
parser.add_argument('input', metavar='FILE', help='Trained model H5 file', type=str)
parser.add_argument('output', metavar='DIR', help='Output directory', type=str)
args = parser.parse_args()

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

signal_masses = resonant_signal_masses
has_mass_column = True

output_folder = args.output
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

dataset = DatasetManager(inputs, resonant_weights, cut)
dataset.load_resonant_signal(masses=signal_masses, add_mass_column=has_mass_column, fraction=1)
dataset.load_backgrounds(add_mass_column=has_mass_column)
dataset.split()

model = keras.models.load_model(args.input)

draw_resonant_training_plots(model, dataset, output_folder, split_by_mass=has_mass_column)
