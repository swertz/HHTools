import ROOT as R
import copy, sys, os, inspect 

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
sys.path.append(os.path.join(scriptDir, "../histFactory_hh"))
from basePlotter import *

plots = []
includes = []
code_before_loop = ""

# Needed to evaluate MVA outputs
includes.append( os.path.join(scriptDir, "..", "common", "readMVA.h") )

# For cluster reweighting
includes.append( os.path.join(scriptDir, "..", "common", "reweight_v1tov3.h") )

code_before_loop += """
getBenchmarkReweighter("/home/fynu/sbrochet/scratch/Framework/CMSSW_8_0_6/src/cp3_llbb/HHTools/scripts/", 0, 11);
"""

sample_weights = {}
for node in range(1, 13):
    sample_weights[ "cluster_node_" + str(node) ] = "getBenchmarkReweighter().getWeight({}-1, hh_gen_mHH, hh_gen_costhetastar)".format(node)

# Plot configuration

# llbb 
basePlotter = BasePlotter(baseObjectName = "hh_llmetjj_HWWleptons_btagM_csv", btagWP_str = 'medium', objects = "nominal")
weights_llbb = []
flavour = "All"
categories_llbb = [flavour]
stage_llbb = "no_cut"
plots_llbb = ["mll", "mjj", "basic", "bdtinput", "ht", "other", "llidisoWeight", 'jjbtagWeight', 'trigeffWeight', 'puWeight', 'forSkimmer', 'csv']
#plots_llbb += ["bdtoutput"]
plots.extend(basePlotter.generatePlots(categories_llbb, stage_llbb, systematic = "nominal", weights = weights_llbb, requested_plots = plots_llbb))

tree = {}
tree["name"] = "t"
tree["cut"] = basePlotter.joinCuts(basePlotter.sanityCheck, basePlotter.dict_cat_cut["All"])
tree["branches"] = []

for plot in plots :
    branch = {}
    branch["name"] = plot["name"].split("_"+flavour)[0]
    branch["variable"] = plot["variable"]
    tree["branches"].append(branch)
    
for banch in tree["branches"] :
    print banch
