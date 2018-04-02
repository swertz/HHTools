import numpy as np

import matplotlib
matplotlib.use('pdf')

import matplotlib.pyplot as plt
from sklearn import metrics

from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import matplotlib.colors as colors

import os

def binDataset(dataset, weights, bins, range=None, norm=False):
    """
    Bin a dataset

    Parameters:
        dataset: a numpy array of data to bin
        weights: data weights
        bins: either a list of bin boundaries or the number of bin to user
        range: The lower and upper range of the bins. If not provided, range is simply (a.min(), a.max()). Values outside the range are ignored

    Returns:
        a tuple (hist, errors, bin_edges):
    """

    # First, bin dataset
    hist, bin_edges = np.histogram(dataset, bins=bins, range=range, weights=weights)

    # Bin weights^2 to extract the uncertainty
    squared_errors, _ = np.histogram(dataset, weights=np.square(weights), bins=bin_edges)
    errors = np.sqrt(squared_errors)

    if norm:
        norm_factor = np.diff(bin_edges) * hist.sum()
        hist /= norm_factor
        errors /= norm_factor

    return (hist, errors, bin_edges)

def drawTestingOnRanges(**kwargs):
    background_data = kwargs.get('testing_background_data')
    signal_data = kwargs.get('testing_signal_data')

    # Weights, optional
    background_weights = kwargs.get('testing_background_weights', None)
    signal_weights = kwargs.get('testing_signal_weights', None)

    # Different cuts
    background_indices = kwargs.get('testing_background_indices')
    signal_indices = kwargs.get('testing_signal_indices')

    indices_ranges = kwargs['indices_ranges']
    
    x_range = kwargs.get('range')
    bins = kwargs.get('bins', 50)
    x_label = kwargs.get('x_label', '')
    output_file = kwargs.get('output')

    nranges = len(signal_indices)

    fig = plt.figure(1, figsize=(7, 7), dpi=300)

    # Create an axes instance
    ax = fig.add_subplot(111)

    background_color = '#B64926'
    signal_color = '#468966'

    background_colors = ["#41bbc5", "#723240", "#b3e467"]

    # Testing data
    #background_hists = []
    #signal_hists = []
    #
    #bkg_hist, _, bin_edges = binDataset(background_data[background_indices[0]], background_weights[background_indices[0]], bins=bins, range=x_range, norm=True)
    #sig_hist, _, _ = binDataset(signal_data[signal_indices[0]], signal_weights[signal_indices[0]], bins=bin_edges, norm=True)
    #background_hists.append(bkg_hist)
    #signal_hists.append(sig_hist)
    #
    #for i in range(1, nranges):
    #    background_hists.append(binDataset(background_data[background_indices[i]], background_weights[background_indices[i]], bins=bin_edges, norm=True)[0])
    #    signal_hists.append(binDataset(signal_data[signal_indices[i]], signal_weights[signal_indices[i]], bins=bin_edges, norm=True)[0])

    #bin_centers = (bin_edges[1:] + bin_edges[:-1]) / 2
    #bin_width = bin_edges[1] - bin_edges[0]

    #for i in range(nranges):
    #    ax.step(bin_centers, background_hists[i], lw=2, where='mid', label='Background (training) -- range {}'.format(i), color=background_color)
    #    ax.step(bin_centers, signal_hists[i], lw=2, where='mid', label='Signal (training) -- range {}'.format(i), color=signal_color)

    for i in range(nranges):
        ax.hist(background_data[background_indices[i]], bins, x_range, normed=True, weights=background_weights[background_indices[i]], histtype='step', color=background_colors[i], label='Background {}'.format(indices_ranges[i]), lw=3)
        #ax.hist(signal_data[signal_indices[i]], bins, x_range, normed=True, weights=signal_weights[signal_indices[i]], histtype='step', color=signal_color, label='Signal (training) -- range {}')
    
    ax.margins(x=0.1)
    ax.set_ylim(ymin=0)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], ncol=2, numpoints=1, loc='best', frameon=False)

    ax.set_xlabel(x_label)

    fig.set_tight_layout(True)

    fig.savefig(output_file)

    plt.close()
    

def drawTrainingTestingComparison(**kwargs):
    training_background_data = kwargs.get('training_background_data')
    training_signal_data = kwargs.get('training_signal_data')
    testing_background_data = kwargs.get('testing_background_data')
    testing_signal_data = kwargs.get('testing_signal_data')

    # Weights, optional
    training_background_weights = kwargs.get('training_background_weights', None)
    training_signal_weights = kwargs.get('training_signal_weights', None)
    testing_background_weights = kwargs.get('testing_background_weights', None)
    testing_signal_weights = kwargs.get('testing_signal_weights', None)

    range = kwargs.get('range')
    bins = kwargs.get('bins', 50)
    x_label = kwargs.get('x_label', '')
    output_file = kwargs.get('output')

    def makeErrorBoxes(ax, xdata, ydata, yerror, bin_width, ec='None', alpha=0.2):
        # Create list for all the error patches
        errorboxes = []

        # Loop over data points; create box from errors at each point
        for xc, yc, ye in zip(xdata, ydata, yerror):
            rect = Rectangle((xc - bin_width / 2, yc - ye), bin_width, 2*ye)
            errorboxes.append(rect)

        # Create patch collection with specified colour/alpha
        pc = PatchCollection(errorboxes, linewidth=0, facecolor='none', edgecolor=ec, hatch='/////', alpha=alpha)

        # Add collection to axes
        ax.add_collection(pc)

    fig = plt.figure(1, figsize=(7, 7), dpi=300)

    # Create an axes instance
    ax = fig.add_subplot(111)

    background_color = '#B64926'
    signal_color = '#468966'

    # Training data
    training_background_histogram, training_background_errors, bin_edges = binDataset(training_background_data, training_background_weights, bins=bins, range=range, norm=True)
    training_signal_histogram, training_signal_errors, _ = binDataset(training_signal_data, training_signal_weights, bins=bin_edges, norm=True)

    # Testing data
    testing_background_histogram, testing_background_errors, _ = binDataset(testing_background_data,testing_background_weights, bins=bin_edges, norm=True)
    testing_signal_histogram, testing_signal_errors, _ = binDataset(testing_signal_data,testing_signal_weights, bins=bin_edges, norm=True)

    bin_centers = (bin_edges[1:] + bin_edges[:-1]) / 2
    bin_width = bin_edges[1] - bin_edges[0]

    ax.bar(bin_centers, training_background_histogram, lw=0, align='center', alpha=0.5, label='Background (training)', color=background_color, width=bin_width)
    makeErrorBoxes(ax, bin_centers, training_background_histogram, training_background_errors, bin_width, ec=background_color, alpha=0.7)

    ax.bar(bin_centers, training_signal_histogram, lw=0, align='center', alpha=0.5, label='Signal (training)', color=signal_color, width=bin_width)
    makeErrorBoxes(ax, bin_centers, training_signal_histogram, training_signal_errors, bin_width, ec=signal_color, alpha=0.7)

    ax.errorbar(bin_centers, testing_background_histogram, yerr=testing_background_errors, linestyle='', marker='o', mew=0, mfc=background_color, ecolor=background_color, label='Background (testing)')
    ax.errorbar(bin_centers, testing_signal_histogram, yerr=testing_signal_errors, linestyle='', marker='o', mew=0, mfc=signal_color, ecolor=signal_color, label='Signal (testing)')

    ax.margins(x=0.1)
    ax.set_ylim(ymin=0)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], ncol=2, numpoints=1, loc='best', frameon=False)

    ax.set_xlabel(x_label)

    fig.set_tight_layout(True)

    fig.savefig(output_file)

    plt.close()

    # return n_background, n_signal
    
def drawNNOutput(background_training_predictions, background_testing_predictions,
                 signal_training_predictions, signal_testing_predictions,
                 background_training_weights, background_testing_weights,
                 signal_training_weights, signal_testing_weights,
                 output_dir=".", output_name="nn_output.pdf",
                 bins=50,
                 testing_signal_indices=None, testing_background_indices=None, indices_ranges=None
                 ):

    drawTrainingTestingComparison(
            training_background_data=background_training_predictions,
            training_signal_data=signal_training_predictions,
            testing_background_data=background_testing_predictions,
            testing_signal_data=signal_testing_predictions,

            training_background_weights=background_training_weights,
            training_signal_weights=signal_training_weights,
            testing_background_weights=background_testing_weights,
            testing_signal_weights=signal_testing_weights,

            bins=bins,
            range=[0, 1],
            x_label="NN output",
            output=os.path.join(output_dir, output_name)
            )
    
    drawTestingOnRanges(
            testing_background_data=background_testing_predictions,
            testing_signal_data=signal_testing_predictions,

            testing_background_weights=background_testing_weights,
            testing_signal_weights=signal_testing_weights,

            testing_background_indices=testing_background_indices,
            testing_signal_indices=testing_signal_indices,
            indices_ranges=indices_ranges,
            
            bins=bins,
            range=[0, 1],
            x_label="NN output",
            output=os.path.join(output_dir, "ranges_" + output_name)
            )

def drawNNVersusVar(predictions, var, weights, bins, output_dir=".", output_name="nn_output_vs_var.pdf", logZ=False):
    fig = plt.figure(1, figsize=(6, 6), dpi=300)
    ax = fig.add_subplot(111)
    
    hist, xedges, yedges = np.histogram2d(predictions, var, bins=bins, weights=weights)
    X, Y = np.meshgrid(xedges, yedges)
    if logZ:
        cm = ax.pcolormesh(X, Y, hist.T, norm=colors.LogNorm(vmin=hist.min() + 1e-3, vmax=hist.max()))
    else:
        cm = ax.pcolormesh(X, Y, hist.T)
    fig.colorbar(cm)
    fig.text(0.05, 0.95, "Pearson r: {}".format(np.corrcoef([predictions, var])[1,0]), bbox={"facecolor": "white"})

    fig.savefig(os.path.join(output_dir, output_name))

    plt.close()

def draw2D(x_var, y_var, weights, bins, output_dir=".", output_name="nn_output_vs_var.pdf", x_label=None, y_label=None, title=None, fig_callbacks=[], data_callbacks=[], normed=False, logZ=False, **kwargs):
    fig = plt.figure(1, figsize=(8, 7), dpi=300)
    fig.suptitle(title)
    ax = fig.add_subplot(111)
    
    hist, xedges, yedges = np.histogram2d(x_var, y_var, bins=bins, weights=weights, normed=normed)

    for f in data_callbacks:
        hist, xedges, yedges = f(hist, xedges, yedges)
    
    X, Y = np.meshgrid(xedges, yedges)

    norm=None
    if logZ:
        hist = np.clip(hist, np.min(hist[hist>0]), np.max(hist))
        norm=colors.LogNorm(vmin=hist.min(), vmax=hist.max())
    
    cm = ax.imshow(hist.T, origin='lower', norm=norm, extent=[min(xedges), max(xedges), min(yedges), max(yedges)], aspect='auto', **kwargs)

    #cm = ax.pcolormesh(X, Y, hist.T, norm=colors.LogNorm(vmin=hist.min() + 1e-10, vmax=hist.max()), shading='gouraud', **kwags)
    
    ax.set_xlabel(x_label, fontsize='large')
    ax.set_ylabel(y_label, fontsize='large')
    ax.margins(0.05)

    for f in fig_callbacks:
        f(fig, ax, cm, x_var, y_var)

    fig.savefig(os.path.join(output_dir, output_name))
    
    plt.close()

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
        skimmed_data = data[from_:]
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
    auc = metrics.auc(x, y, reorder=True)

    fig = plt.figure(1, figsize=(6, 6), dpi=300)
    fig.clear()

    # Create an axes instance
    ax = fig.add_subplot(111)

    ax.plot(x, y, '-', color='#B64926', lw=2, label="AUC: %.4f" % auc)
    ax.plot([0, 1], [0, 1], ':', color='black', lw=2, label="Random cut")
    ax.margins(0.05)

    ax.set_xlabel("Background efficiency")
    ax.set_ylabel("Signal efficiency")
    
    fig.set_tight_layout(True)

    ax.legend(loc='lower right', numpoints=1, frameon=False)

    print("AUC: %.4f" % auc)

    fig.savefig(os.path.join(output_dir, output_name))

    plt.close()

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

def draw_keras_history(history, output_dir='.', output_name='loss.pdf'):
    """
    Plot loss value for training and validation samples

    Argument:
      history:  Keras training history
    """

    fig = plt.figure(1, figsize=(6, 6), dpi=300)
    fig.clear()

    # Create an axes instance
    ax = fig.add_subplot(111)

    if 'loss' in history.history.keys():
        training_losses = history.history['loss']
        epochs = np.arange(0, len(training_losses))
        l1 = ax.plot(epochs, training_losses, '-', color='#8E2800', lw=2, label="Training loss")
    
    if 'val_loss' in history.history.keys():
        validation_losses = history.history['val_loss']
        epochs = np.arange(0, len(validation_losses))
        l2 = ax.plot(epochs, validation_losses, '-', color='#468966', lw=2, label="Validation loss")

    ax.set_xlabel("Epochs")
    ax.set_ylabel("Loss")
    
    # training_acc = history.history['acc']
    # validation_acc = history.history['val_acc']

    # ax2 = ax.twinx()
    # l3 = ax2.plot(epochs, training_acc, '--', color='#8E2800', lw=2, label="Training accuracy")
    # l4 = ax2.plot(epochs, validation_acc, '--', color='#468966', lw=2, label="Validation accuracy")
    # ax2.set_ylabel("Accuracy")

    ax.margins(0.05)
    # ax2.margins(0.05)

    fig.set_tight_layout(True)

    # lns = l1 + l2 + l3 + l4
    #lns = l1 + l2
    #labs = [l.get_label() for l in lns]
    #ax.legend(lns, labs, loc='best', numpoints=1, frameon=False)
    ax.legend(loc='best', numpoints=1, frameon=False)

    fig.savefig(os.path.join(output_dir, output_name))

    plt.close()

def drawDNNFlux(masses, predictions, title="", output_dir=".", output_name="flux.pdf"):
    fig = plt.figure(1, figsize=(7, 7), dpi=300)
    fig.clear()
    fig.suptitle(title)

    ax = fig.add_subplot(111)
   
    colormap = plt.cm.coolwarm
    plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 0.9, len(predictions))])

    for i,event in enumerate(predictions):
        dic = {}
        if i == len(predictions) - 1:
            dic["label"] = "One event"
        ax.plot(masses, predictions[i], lw=1, **dic)

    ax.set_xlabel("Mass input (GeV)")
    ax.set_ylabel("DNN output")
    ax.legend()
    fig.savefig(os.path.join(output_dir, output_name))

    plt.close()

def plotHistories(loss_history, output_dir, output_name):
    fig, ax = plt.subplots(3, 1, dpi=300)

    values = np.array(loss_history["d"])
    ax[0].plot(range(len(values)), values, color="blue")
    #ax[0].legend(loc="upper right")
    ax[0].set_ylabel("Discr. loss")
    
    values = np.array(loss_history["a"])
    ax[1].plot(range(len(values)), values, color="green")
    #ax[1].legend(loc="lower right")
    ax[1].set_ylabel("Advers. loss")

    values = np.array(loss_history["f"])
    ax[2].plot(range(len(values)), values, color="red")
    #ax[2].legend(loc="lower right")
    ax[2].set_ylabel("Total loss")
    ax[2].set_xlabel("Iterations")
    
    fig.set_tight_layout(True)
    fig.savefig(os.path.join(output_dir, output_name))

    plt.close()

def drawPredictedRatio(discr, advers, data, nuisance, targets, weights, folder, output, only_bkg=False, n_bins=200, scaling=10):
    targets = targets[:,0].astype(bool)
    sum_wgt_sig = np.sum(weights[targets])
    sum_wgt_bkg = np.sum(weights[~targets])
    # Make sure signals and backgrounds are normalised
    weights[~targets] /= sum_wgt_bkg
    weights[targets] /= sum_wgt_sig
    
    if only_bkg:
        data = data[~targets]
        nuisance = nuisance[~targets]
        weights = weights[~targets]

    fig = plt.figure(1, figsize=(6, 6), dpi=300)
    fig.clear()

    ax = fig.add_subplot(111)

    reg_0 = nuisance#[:,0].astype(bool)
    #reg_1 = nuisance[:,1].astype(bool)

    scores = discr.predict(data, batch_size=20000)

    hist_0, bins, _ = ax.hist(scores[reg_0], n_bins, (0,1), weights=scaling*weights[reg_0], histtype='step', label='Region 1')
    total, _, _ = ax.hist(scores, bins, weights=scaling*weights, histtype='step', label='Total')

    #total = hist_0 + hist_1
    ratio = np.true_divide(hist_0, total)

    bin_center = 0.5*(bins[0:-1] + bins[1:])
    pred_ratio = advers.predict(bin_center)[:,0]
    ax.plot(bin_center, pred_ratio, label='Advers output')

    ax.plot(bin_center, ratio, 'o', label='Hist ratio')

    ax.legend()
    fig.savefig(os.path.join(folder, output))
    plt.close()
