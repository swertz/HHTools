import ROOT as R
import copy, sys, os, inspect 

scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
sys.path.append(os.path.join(scriptDir, "../histFactory_hh"))

from basePlotter import *

include_directories = []
plots = []
library_directories = []
libraries = []

include_directories.append(os.path.join(scriptDir, "..", "common"))

headers = default_headers()

code_before_loop = default_code_before_loop()
code_in_loop = default_code_in_loop()
code_after_loop = default_code_after_loop()

sample_weights = {}
# for node in range(1, 13):
    # sample_weights[ "cluster_node_" + str(node) ] = "getBenchmarkReweighter().getWeight({}-1, hh_gen_mHH, hh_gen_costhetastar)".format(node)

# Plot configuration

weights_llbb = []
flavour = "All"
categories_llbb = [flavour]
stage_llbb = "no_cut"
plots_llbb = ["mll", "mjj", "basic", "bdtinput", "ht", "other", "llidisoWeight", 'jjbtagWeight', 'trigeffWeight', 'puWeight', 'DYNobtagToBTagMWeight', 'forSkimmer', 'cmva', 'gen', 'evt', 'detailed_flavour']
# plots_llbb += ["bdtoutput"]

def plots_to_branches(plots, tree):
    for plot in plots:
        # Ignore 2D plots
        if ':::' in plot["variable"]:
            continue

        branch = {}
        branch["name"] = plot["name"].split("_"+flavour)[0]
        branch["variable"] = plot["variable"]
        if 'type' in plot:
            branch['type'] = plot['type']

        tree["branches"].append(branch)
