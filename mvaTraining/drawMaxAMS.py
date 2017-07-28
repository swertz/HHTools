import plotTools
from common import *
import argparse
import keras
import numpy as np
from scipy import interpolate
from math import sqrt, log
import matplotlib.pyplot as plt
from sklearn import metrics

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', metavar='DIR', help='Output directory', type=str, default=".")
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

LUMI = 35900
SYST_B = 0.05
n_bins = 50 # use 3000 for AMS plots

#resonant_signal_masses = [400]

models = {

        'all': {
            'file': 'hh_resonant_trained_models/2017-07-04_260_270_300_350_400_450_500_550_600_650_750_800_900_latest_march_prod_100epochs_REPLAY/hh_resonant_trained_model.h5',
            'legend': 'Parameterised training with all masses',
            'no_mass_column': False,
            'color': '#1f77b4',
            'ls': '-.'
            },

        'dedicated': [

            {
                'file': 'hh_resonant_trained_models/2017-07-05_260_270_300_350_400_450_500_550_600_650_750_800_900_latest_march_prod_100epochs_NOMASS/hh_resonant_trained_model.h5',
                'legend': 'Regular training with all masses',
                'color': '#17becf',
                'ls': '--',
                'no_mass_column': True
            },

            {
                #'file': 'hh_resonant_trained_models/2017-01-24_400_dy_estimation_from_BDT_new_prod_on_GPU_deeper_100epochs/hh_resonant_trained_model.h5',
                'file': 'hh_resonant_trained_models/2017-07-04_400_latest_march_prod_100epochs_REPLAY/hh_resonant_trained_model.h5',
                'legend': 'Dedicated training for M=400 GeV',
                'color': '#ff7f0e',
                'ls': '-',
                'no_mass_column': True
            },

            {
                #'file': 'hh_resonant_trained_models/2017-01-24_900_dy_estimation_from_BDT_new_prod_on_GPU_deeper_100epochs/hh_resonant_trained_model.h5',
                'file': 'hh_resonant_trained_models/2017-07-04_900_latest_march_prod_100epochs_REPLAY/hh_resonant_trained_model.h5',
                'legend': 'Dedicated training for M=900 GeV',
                'color': '#2ca02c',
                'ls': '-',
                'no_mass_column': True
            },

            {
                #'file': 'hh_resonant_trained_models/2017-02-03_260_300_400_550_800_900_dy_estimation_from_BDT_new_prod_on_GPU_deeper_100epochs/hh_resonant_trained_model_updated.h5',
                'file': 'hh_resonant_trained_models/2017-07-05_260_270_300_350_400_450_500_550_600_750_800_900_latest_march_prod_100epochs_REPLAY/hh_resonant_trained_model.h5',
                'legend': 'Parameterised training with all masses\nexcept 650 GeV',
                'color': '#d62728',
                'ls': ':',
                'no_mass_column': False
            },
            

        ]

    }

expected_limits = {
        260: 1, #266,
        270: 1, #317,
        300: 1, #342,
        350: 1, #224,
        400: 1, #131,
        450: 1, #75.6,
        500: 1, #51.4,
        550: 1, #37.6,
        600: 1, #28.6,
        650: 1, #22.5,
        700: 1, #20.2,
        750: 1, #17.7,
        800: 1, #16.1,
        850: 1, #14.8,
        900: 1, #13.7
    }

output_folder = args.output
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

models['all']['model'] = keras.models.load_model(models['all']['file'])
for m in models['dedicated']:
    m['model'] = keras.models.load_model(m['file'])

dataset = DatasetManager(inputs, resonant_weights, cut)
dataset.load_resonant_signal(masses=resonant_signal_masses, add_mass_column=True, fraction=1, reweight_to_cross_section=True)
dataset.load_backgrounds(add_mass_column=True)

def get_AMS(s, b, sigma_b=0):
    def error():
        print("Warning: got negative argument for s, b, sigma = {}, {}, {}".format(s, b, sigma_b))

    if s == 0:
        return 0
    if s < 0 or b < 0 or sigma_b <= 0:
        error()
        return None
    
    var_b = sigma_b**2
    b0 = 0.5 * (b - var_b + sqrt((b - var_b)**2 + 4 * (s + b) * var_b))
    
    if b0 <= 0:
        error()
        return None
    
    arg = 2 * ((s + b) * log((s + b) / b0) - s - b + b0) + (b - b0)**2 / var_b
    
    if arg < 0:
        error()
        return None
    
    return sqrt(arg)

def get_stat_uncertainty(n, n_MC):
    weight = n / n_MC
    return weight * sqrt(n_MC)

def get_AMS_binned(sig_binned, bkg_binned):
    AMS = []
    cuts = []

    sig_hist = sig_binned[0]
    bkg_hist = bkg_binned[0]
    sig_hist_sq = sig_binned[1]
    bkg_hist_sq = bkg_binned[1]

    # Assume everybody has the same edges
    edges = sig_binned[2]

    for i in range(len(sig_hist) + 1):
        sig_sum = np.sum(sig_hist[i:])
        bkg_sum = np.sum(bkg_hist[i:])
        
        bkg_sigma = sqrt(np.sum(bkg_hist_sq[i:]))
        bkg_sigma = sqrt(bkg_sigma**2 + SYST_B * bkg_sum)
        
        ams = get_AMS(sig_sum, bkg_sum, bkg_sigma)
        if ams is not None:
            AMS.append(ams)
            cuts.append(edges[i])

    return (np.array(AMS), np.array(cuts))

def get_max_AMS(sig_binned, bkg_binned):
    return np.max(get_AMS_binned(sig_binned, bkg_binned)[0])

def get_ROC_AUC(sig_binned, bkg_binned):
    x, y = plotTools.get_roc(sig_binned[0], bkg_binned[0])
    return metrics.auc(x, y, reorder=True) 

def get_FOM_vs_mass(mod, dataset, FOM_callable):
    print("Doing model {}".format(mod['file']))

    FOMs = []

    sig = dataset.signal_dataset
    sig_weights = dataset.signal_weights
    bkg = dataset.background_dataset
    bkg_weights = dataset.background_weights

    for m in resonant_signal_masses:
        print("Doing mass {}...".format(m))
    
        # Only keep events with that mass for the signal
        sig_mask = sig[:,-1] == m
        sig_m = sig[sig_mask]
        if mod['no_mass_column']:
            sig_m = sig_m[:,:-1]
        sig_pred_m = mod['model'].predict(sig_m, batch_size=20000)[:,0]
        sig_weights_m = expected_limits[m] * sig_weights[sig_mask]
    
        # For the background, set the mass input to that of the signal
        # We need ALL the background events to ensure proper normalisation to cross section
        bkg_m = bkg
        bkg_m[:,-1] = m
        if mod['no_mass_column']:
            bkg_m = bkg[:,:-1]
        bkg_pred_m = mod['model'].predict(bkg_m, batch_size=20000)[:,0]
    
        # Also histograms without weights to compute the statistical uncertainty on MC
        sig_binned = plotTools.binDataset(sig_pred_m, LUMI * sig_weights_m, bins=n_bins, range=[0,1])
        bkg_binned = plotTools.binDataset(bkg_pred_m, LUMI * bkg_weights, bins=n_bins, range=[0,1])
        
        FOM = FOM_callable(sig_binned, bkg_binned)
    
        FOMs.append(FOM)

    return FOMs


DO_AMS = False
DO_EXCL_AMS = True
DO_ROC_AUC = False
DO_AMS_PLOTS = False

if DO_AMS:

    fig = plt.figure(1, figsize=(7, 7))
    ax = fig.add_subplot(111)
    
    all_max_AMS = get_FOM_vs_mass(models['all'], dataset, get_max_AMS)
    ax.plot(resonant_signal_masses, all_max_AMS, color=models['all']['color'], lw=2, label=models['all']['legend'])
    
    for mod in models['dedicated']:
        max_AMS = get_FOM_vs_mass(mod, dataset, get_max_AMS)
        ax.plot(resonant_signal_masses, max_AMS, color=mod['color'], lw=2, label=mod['legend'])
    
    ax.set_ylabel("Maximum AMS", fontsize='large')
    ax.set_xlabel("Signal mass", fontsize='large')
    
    ax.legend()
    ax.margins(0.05)
    
    fig.savefig(os.path.join(args.output, "maxAMS_vs_mass_newTrainingOnly_syst_20fb.pdf"))

    plt.close()

if DO_EXCL_AMS:

    fig = plt.figure(1, figsize=(7, 7))
    ax = fig.add_subplot(111)
    
    all_exp_limit = get_FOM_vs_mass(models['all'], dataset, get_median_expected_limit)
    ax.semilogy(resonant_signal_masses, all_exp_limit, color=models['all']['color'], lw=2, label=models['all']['legend'], ls=models['all']['ls'])
    
    for mod in models['dedicated']:
        max_exp_limit = get_FOM_vs_mass(mod, dataset, get_median_expected_limit)
        ax.semilogy(resonant_signal_masses, max_exp_limit, color=mod['color'], lw=2, label=mod['legend'], ls=mod['ls'])
    
    ax.set_ylabel("Median expected 95% CL limit (fb)", fontsize='large')
    ax.set_xlabel("Signal mass", fontsize='large')
    
    ax.legend()
    ax.margins(0.05)
    
    fig.savefig(os.path.join(args.output, "exp_limit_vs_mass.pdf"))

    plt.close()

if DO_ROC_AUC:

    fig = plt.figure(1, figsize=(7, 7))
    ax = fig.add_subplot(111)
    
    all_max_AMS = get_FOM_vs_mass(models['all'], dataset, get_ROC_AUC)
    ax.plot(resonant_signal_masses, all_max_AMS, color=models['all']['color'], lw=2, label=models['all']['legend'], ls=models['all']['ls'])
    
    for mod in models['dedicated']:
        max_AMS = get_FOM_vs_mass(mod, dataset, get_ROC_AUC)
        ax.plot(resonant_signal_masses, max_AMS, color=mod['color'], lw=2, label=mod['legend'], ls=mod['ls'])

    #y_lim = ax.get_ylim()

    #ax.plot([400,400], y_lim, lw=2, ls='--', color=models['dedicated'][1]['color'])
    #ax.plot([900,900], y_lim, lw=2, ls='--', color=models['dedicated'][2]['color'])
    #ax.plot([650,650], y_lim, lw=2, ls='--', color=models['dedicated'][3]['color'])
    ax.set_ylim([0.7, 1.02])
    
    ax.set_ylabel("ROC a.u.c.", fontsize='large')
    ax.set_xlabel("Signal mass", fontsize='large')
    
    ax.legend().get_frame().set_alpha(1)
    
    fig.savefig(os.path.join(args.output, "ROCAUC_vs_mass_newTrainingOnly.pdf"))

    plt.close()

if DO_AMS_PLOTS:

    ams_hists_models = []
    
    ams_hists_models.append((get_FOM_vs_mass(models['all'], dataset, get_AMS_binned), models['all']))
    
    for mod in models['dedicated']:
        ams_hists_models.append((get_FOM_vs_mass(mod, dataset, get_AMS_binned), mod))

    for i, m in enumerate(resonant_signal_masses):
        fig = plt.figure(1, figsize=(7, 7))
        fig.suptitle("Signal mass: {} GeV".format(m))
        ax = fig.add_subplot(111)

        for ams, mod in ams_hists_models:
            nn_cuts = ams[i][1]
            ax.plot(nn_cuts, ams[i][0], color=mod['color'], lw=1, label=mod['legend'])
        
        ax.set_ylabel("AMS", fontsize='large')
        ax.set_xlabel("Cut on NN", fontsize='large')
        
        ax.legend()
        ax.margins(0.05)
        
        fig.savefig(os.path.join(args.output, "AMS_vs_cut_M{}.pdf".format(m)))

        plt.close()
