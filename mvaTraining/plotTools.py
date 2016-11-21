import numpy as np

import matplotlib
matplotlib.use('pdf')

import matplotlib.pyplot as plt
from sklearn import metrics

import os

def binPredictions(predictions, weights, bins=None, range=None):
    return np.histogram(predictions, bins=bins, range=range, density=True, weights=weights)
    
def drawNNOutput(background_training_predictions, background_testing_predictions,
                 signal_training_predictions, signal_testing_predictions,
                 background_training_weights, background_testing_weights,
                 signal_training_weights, signal_testing_weights,
                 output_dir=".", output_name="nn_output.pdf"
                 ):

    fig = plt.figure(1, figsize=(7, 7), dpi=300)

    # Create an axes instance
    ax = fig.add_subplot(111)

    background_color='#B64926'
    signal_color='#468966'

    # Training predictions
    n_background, bins, background_patches = ax.hist(background_training_predictions, 50, range=[0, 1], normed=1, alpha=0.5, label='Background (training)', color=background_color, lw=0, histtype='stepfilled', weights=background_training_weights)
    n_signal, _, signal_patches = ax.hist(signal_training_predictions, bins=bins, alpha=0.5, normed=1, label='Signal (training)', color=signal_color, histtype='stepfilled', lw=0, weights=signal_training_weights)

    # Testing predictions
    signal_testing_histogram, _ = np.histogram(signal_testing_predictions, bins=bins, density=True, weights=signal_testing_weights)

    background_testing_histogram, _ = np.histogram(background_testing_predictions, bins=bins, density=True, weights=background_testing_weights)

    ax.plot((bins[1:] + bins[:-1]) / 2, background_testing_histogram, linestyle='', marker='o', mew=0, mfc=background_color, label='Background (testing)')
    ax.plot((bins[1:] + bins[:-1]) / 2, signal_testing_histogram, linestyle='', marker='o', mew=0, mfc=signal_color, label='Signal (testing)')

    ax.legend(ncol=2, numpoints=1, loc=1, frameon=False)

    ax.set_xlabel('NN output')

    fig.set_tight_layout(True)

    fig.savefig(os.path.join(output_dir, output_name))

    plt.close()

    return n_background, n_signal

def get_roc(signal, background):
    """
    Compute ROC

    Arguments:
        signal, background: an array of discriminant, one for each event

    Return:
        x, y
    """

    n_points = len(signal)

    def get_efficiency(data, from_):
        # print data
        skimmed_data = data[from_:]
        # print np.sum(skimmed_data), np.sum(data), np.sum(skimmed_data) / np.sum(data)
        return np.sum(skimmed_data) / np.sum(data)

    x = []
    y = []
    for i in range(n_points):
        y.append(get_efficiency(signal, i))
        x.append(get_efficiency(background, i))

    x = np.asarray(x)
    y = np.asarray(y)

    order = np.lexsort((y, x))
    x, y = x[order], y[order]

    return x, y

def draw_roc(signal, background, output_dir=".", output_name="roc.pdf"):
    """
    Draw a ROC curve

    Arguments:
    signal, background: an array of discriminant, one for each event
    """

    x, y = get_roc(signal, background)

    fig = plt.figure(1, figsize=(7, 7), dpi=300)
    fig.clear()

    # Create an axes instance
    ax = fig.add_subplot(111)

    ax.plot(x, y, '-', color='#B64926', lw=2)
    ax.margins(0.05)

    ax.set_xlabel("Background efficiency")
    ax.set_ylabel("Signal efficiency")
    
    fig.set_tight_layout(True)

    fig.savefig(os.path.join(output_dir, output_name))

    plt.close()

    print("AUC: %f" % metrics.auc(x, y, reorder=True))

    def get_index(y, value):
        """
        Find the last index of the element in y
        satistying y[index] <= value
        """

        for i in range(len(y)):
            if y[i] <= value:
                continue

            return i

    print("Background efficiency for signal efficiency of 0.70: %f" % x[get_index(y, 0.70)])
    print("Background efficiency for signal efficiency of 0.80: %f" % x[get_index(y, 0.80)])
    print("Background efficiency for signal efficiency of 0.90: %f" % x[get_index(y, 0.90)])
