import ROOT as R
import copy, sys, os, inspect 

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
sys.path.append(os.path.join(scriptDir, "../histFactory_hh"))
from basePlotter import *
#includes = ["/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/HHTools/histFactory_hh/readMVA.h"]

plots = []

# llbb 
basePlotter = BasePlotter(mode = "custom", baseObjectName = "hh_llmetjj_HWWleptons_btagM_csv", btagWP_str = 'medium', objects = "nominal")
weights_llbb = []
flavour = "All"
categories_llbb = [flavour]
stage_llbb = "no_cut"
plots_llbb = ["mll", "mjj", "basic", "bdtinput", "ht", "other", "llidisoWeight", 'jjbtagWeight', 'trigeffWeight', 'puWeight', 'forSkimmer', 'csv']
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
