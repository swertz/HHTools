import plotTools
from common import *
import argparse
import keras
import numpy as np
from scipy import interpolate

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
dataset.load_resonant_signal(masses=resonant_signal_masses, add_mass_column=True, fraction=1)

DO_SIG = True
DO_SIG_INDIV = True
DO_BKG = True

def add_random_mass_column(a):
    """Add random mass values to a as an extra column"""
    n_evt = len(a)
    m_min = min(resonant_signal_masses)
    m_max = max(resonant_signal_masses)
    masses = m_min + (m_max - m_min) * np.random.rand(n_evt, 1)
    a = np.hstack([a, masses])
    return a

if DO_BKG:
    dataset.load_backgrounds(add_mass_column=False)
    
    print("Shaping background...")
    
    # Repeat the background sample
    bkg = np.repeat(dataset.background_dataset, 10, axis=0)
    bkg_weights = np.repeat(dataset.background_weights, 10, axis=0)
    bkg = add_random_mass_column(bkg)
    bkg_predictions = model.predict(bkg, batch_size=20000)[:,0]
    bkg_masses = bkg[:,-1]
    
    print("Plotting background...")

    plotTools.draw2D(bkg_masses, bkg_predictions, bkg_weights, bins=[np.linspace(260, 900, 50), np.linspace(0, 1, 50)], output_dir=args.output, output_name="nn_output_vs_mass_backgrounds.pdf", x_label="Mass input", y_label="NN output", title="Backgrounds", interpolation='bessel', logZ=True, normed=True, fig_callbacks=[
                lambda fig, ax, cm, x_var, y_var: fig.colorbar(cm)
            ]   
        )
    
    plotTools.draw2D(bkg_masses, bkg_predictions, bkg_weights, bins=[np.linspace(260, 900, 50), np.linspace(0.1, 1, 50)], output_dir=args.output, output_name="nn_output_vs_mass_backgrounds_clipped.pdf", x_label="Mass input", y_label="NN output", title="Backgrounds", interpolation='bessel', logZ=True, normed=True, fig_callbacks=[
                lambda fig, ax, cm, x_var, y_var: fig.colorbar(cm)
            ]   
        )

if DO_SIG:

    print("Shaping signal...")

    sig = dataset.signal_dataset
    sig_weights = dataset.signal_weights
    sig_predictions = model.predict(sig, batch_size=20000)[:,0]
    sig_masses = sig[:,-1]

    print("Plotting signal...")

    # Interpolate along mass direction (just as in the analysis)
    def interpolate_1D(new_x):
        interp_x = 0.5 * (new_x[1:] + new_x[:-1])
        def Iinterpolate_1D(hist, x, y):
            x = x[:-1]
            hist = np.vstack([ interpolate.Akima1DInterpolator(x, pred)(interp_x) for pred in hist.T]).T
            return hist, new_x, y
        return Iinterpolate_1D

    # For each mass slice separately, normalise signal output shape
    def normalise_signals(hist, x, y):
        for i in range(hist.shape[0]):
            hist[i,:] = hist[i,:] / np.sum(hist[i,:])
        return hist, x, y
    
    plotTools.draw2D(sig_masses, sig_predictions, sig_weights, bins=[resonant_signal_masses + [1000], np.linspace(0, 1, 50)], output_dir=args.output, output_name="nn_output_vs_mass_signals.pdf", x_label="Mass input & signal mass", y_label="NN output", title="Signals", interpolation='bessel', normed=True, logZ=True, 
            fig_callbacks=[
                lambda fig, ax, cm, x_var, y_var: fig.colorbar(cm)
            ],
            data_callbacks=[
                interpolate_1D(np.concatenate([ np.arange(260, 351, 5), np.arange(360, 901, 20) ])),
                normalise_signals
            ],
        )
    
    plotTools.draw2D(sig_masses, sig_predictions, sig_weights, bins=[resonant_signal_masses + [1000], np.linspace(0.5, 1, 50)], output_dir=args.output, output_name="nn_output_vs_mass_signals_clipped.pdf", x_label="Mass input & signal mass", y_label="NN output", title="Signals", interpolation='bessel', normed=True, logZ=True, 
            fig_callbacks=[
                lambda fig, ax, cm, x_var, y_var: fig.colorbar(cm)
            ],
            data_callbacks=[
                interpolate_1D(np.concatenate([ np.arange(260, 351, 5), np.arange(360, 901, 20) ])),
                normalise_signals
            ],
        )

if DO_SIG_INDIV:

    for m in resonant_signal_masses:
        dataset.load_resonant_signal(masses=[m], add_mass_column=False, fraction=1)
    
        print("Doing signal m={}...".format(m))

        sig = np.repeat(dataset.signal_dataset, 100, axis=0)
        sig_weights = np.repeat(dataset.signal_weights, 100, axis=0)
        sig = add_random_mass_column(sig)
        sig_predictions = model.predict(sig, batch_size=20000)[:,0]
        sig_masses = sig[:,-1]
    
        plotTools.draw2D(sig_masses, sig_predictions, sig_weights, bins=[np.linspace(260, 900, 50), np.linspace(0, 1, 30)], output_dir=args.output, output_name="nn_output_vs_mass_signal_M{}.pdf".format(m), x_label="Mass input", y_label="NN output", title="Signal: $m_X={}$ GeV".format(m), interpolation='bessel', logZ=True, normed=True, fig_callbacks=[
                    lambda fig, ax, cm, x_var, y_var: fig.colorbar(cm)
                ]   
            )


print("Done.")

