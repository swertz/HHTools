import ROOT as R
import copy, sys, os, inspect 

scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
sys.path.append(os.path.join(scriptDir, "../histFactory_hh"))

from basePlotter import *
from TreesDefinition import *

# llbb 
basePlotter = BasePlotter(baseObjectName = "hh_llmetjj_HWWleptons_nobtag_csv", btagWP_str = 'nobtag', objects = "nominal")
plots.extend(basePlotter.generatePlots(categories_llbb, stage_llbb, systematic = "nominal", weights = weights_llbb, requested_plots = plots_llbb))

tree = {}
tree["name"] = "t"
tree["cut"] = basePlotter.joinCuts(basePlotter.sanityCheck, basePlotter.dict_cat_cut["All"])
tree["branches"] = []

plots_to_branches(plots, tree)


llbbPlotter = BasePlotter(baseObjectName = "hh_llmetjj_HWWleptons_btagM_csv", btagWP_str = 'medium', objects = "nominal")

is_llbb = llbbPlotter.joinCuts(llbbPlotter.sanityCheck, llbbPlotter.dict_cat_cut['All'])

tree["branches"].append({
    'name': 'is_llbb',
    'variable': is_llbb
    })

plots = llbbPlotter.generatePlots(categories_llbb, stage_llbb, systematic="nominal", weights=weights_llbb, requested_plots=['jjbtagWeight'])

for plot in plots:
    # Protect each variable by the 'is_llbb' cut
    new_variable = '((%s) ? %s : 1.)' % (is_llbb, plot['variable'])

    branch = {}
    branch["name"] = plot["name"].split("_"+flavour)[0]
    branch["variable"] = new_variable
    if 'type' in plot:
        branch['type'] = plot['type']

    tree["branches"].append(branch)
