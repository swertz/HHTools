import plotTools
from common import *
import argparse
import keras
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', metavar='FILE', help='Trained model H5 file', type=str)
parser.add_argument('-o', '--output', metavar='DIR', help='Output directory', type=str)
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

signal_masses = [ 260, 300, 400, 500, 650, 750, 800, 900 ]
has_mass_column = True
n_events = 25
mass_values = np.linspace(250, 1000, 500)

output_folder = args.output
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Alternative:
#import h5py
#f = h5py.File('model_file.h5', 'r+')
#del f['optimizer_weights']
#f.close()
def load_model(path):
    json_file = open(path + "_arch.json", "r")
    loaded_model_json = json_file.read()
    json_file.close()
    model = keras.models.model_from_json(loaded_model_json)
    model.load_weights(path + "_weights.h5")
    return model

model = load_model(args.input)

dataset = DatasetManager(inputs, resonant_weights, cut)
dataset.load_backgrounds(add_mass_column=False)

def pick_random(d, n, s=42):
    np.random.seed(s)
    indices = np.random.choice(len(d), n, replace=False)
    return d[indices]

def build_flux(data, masses):
    events_flux = []
    for event in data:
        event_with_masses = np.tile(event, (len(masses), 1))
        event_with_masses = np.hstack([event_with_masses, masses.reshape(-1,1)])
        predictions = model.predict(event_with_masses)[:,0]
        events_flux.append(predictions)
    return events_flux

bkg = dataset.background_dataset
bkg = pick_random(bkg, n_events)
bkg_flux = build_flux(bkg, mass_values)

plotTools.drawDNNFlux(mass_values, bkg_flux, title="Background: TTbar", output_dir="testFlux", output_name="flux_TTbar.pdf")

for signal in signal_masses:
    dataset.load_resonant_signal(masses=[signal], add_mass_column=False, fraction=1)

    sig = dataset.signal_dataset
    sig = pick_random(sig, n_events)
    sig_flux = build_flux(sig, mass_values)

    plotTools.drawDNNFlux(mass_values, sig_flux, title="Signal: $m_X = {}$ GeV".format(signal), output_dir="testFlux", output_name="flux_M{}.pdf".format(signal))
