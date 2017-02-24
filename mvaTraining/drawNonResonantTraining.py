import glob
import os
import pickle
import gzip
import datetime
import argparse

import plotTools

from common import *

import keras

parser = argparse.ArgumentParser(description='Plot NN output and ROC curve of a training for various non-resonant parameters.')
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

parameters_list = nonresonant_parameters
# parameters_list = [(1, 1)]

output_folder = args.output
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

dataset = DatasetManager(inputs, nonresonant_weights, cut)
dataset.load_nonresonant_signal(parameters_list=parameters_list, add_parameters_columns=True)
dataset.load_backgrounds(add_parameters_columns=True)
dataset.split()

model = keras.models.load_model(args.input)

draw_non_resonant_training_plots(model, dataset, output_folder, split_by_parameters=True)
