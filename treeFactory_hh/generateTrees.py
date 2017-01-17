import ROOT as R
import copy, sys, os, inspect 

scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
sys.path.append(os.path.join(scriptDir, "../histFactory_hh"))

from basePlotter import *
from TreesDefinition import *

# llbb 
basePlotter = BasePlotter(baseObjectName = "hh_llmetjj_HWWleptons_btagM_cmva", btagWP_str = 'medium', objects = "nominal")
plots = basePlotter.generatePlots(categories_llbb, stage_llbb, systematic = "nominal", weights = weights_llbb, requested_plots = plots_llbb)

tree = {}
tree["name"] = "t"
tree["cut"] = basePlotter.joinCuts(basePlotter.sanityCheck, basePlotter.dict_cat_cut["All"])
tree["branches"] = []

plots_to_branches(plots, tree)

