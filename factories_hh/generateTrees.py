import ROOT as R
import copy, sys, os, yaml, inspect 

scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
sys.path.append(os.path.join(scriptDir, "../histFactory_hh"))

from basePlotter import *

##### Retrieve config file written by launchHistFactory.py:
config = {}
with open(os.path.join("/tmp", os.getenv("USER") + "_factory.json")) as f:
    config = yaml.safe_load(f)

def get_cfg(var, default=False):
    if var in config.keys():
        return config[var]
    else:
        return default

reweight_signal = get_cfg("reweight_signal")

do_lljj = get_cfg("do_lljj", False)
do_llbb = get_cfg("do_llbb", True)
flavour = get_cfg("flavour", "All")
stage = get_cfg("stage", "no_cut")
branch_families = get_cfg("branches", [])

####### Configure additional content for factory ####
plots = []
library_directories = []
libraries = []
sample_weights = {}

code_before_loop = default_code_before_loop()
code_in_loop = default_code_in_loop()
code_after_loop = default_code_after_loop()
include_directories = default_include_directories(scriptDir)
headers = default_headers()
libraries = default_libraries()
library_directories = default_library_directories()
sources = default_sources(scriptDir)

####### Reweighting -- ME-based -- only for signal #########
if reweight_signal:
    training_grid_reweighter = GridReweighting(scriptDir)

    code_before_loop += training_grid_reweighter.before_loop()
    code_in_loop += training_grid_reweighter.in_loop()
    code_after_loop += training_grid_reweighter.after_loop()
    include_directories += training_grid_reweighter.include_dirs()
    headers += training_grid_reweighter.headers()
    library_directories += training_grid_reweighter.library_dirs()
    libraries += training_grid_reweighter.libraries()
    sources += training_grid_reweighter.sources()
    
    sample_weights["training_grid"] = training_grid_reweighter.sample_weight()

######### Plot configuration ###########

flavour = "All"
categories = [flavour]

plots_for_branches = []
if "basic" in branch_families:
    plots_for_branches += ["mjj", "basic", "nn_inputs", "other", "forSkimmer", "cmva", "evt"]
if "gen" in branch_families:
    plots_for_branches += ["gen"]
if "flavour" in branch_families:
    plots_for_branches += ["detailed_flavour"]
if "weights" in branch_families:
    plots_for_branches += ["llidisoWeight", "jjbtagWeight", "trigeffWeight", "puWeight"]
if "dy_rwgt" in branch_families:
    plots_for_branches += ["dy_rwgt_bdt", "DYNobtagToBTagMWeight"]
if "nn" in branch_families:
    plots_for_branches += ["resonant_nnoutput", "nonresonant_nnoutput"]
 
tree = {}
tree["name"] = "t"
tree["branches"] = []

basePlotter = None

if do_lljj:
    basePlotter = BasePlotter(btag=False)
    
    if do_llbb:
        llbb_temp = BasePlotter(btag=True)
        tree["branches"].append({
            'name': 'is_llbb',
            'variable': llbb_temp.joinCuts(llbb_temp.sanityCheck, llbb_temp.dict_cat_cut[flavour])
            })

else:
    basePlotter = BasePlotter(btag=True)

tree["cut"] = basePlotter.joinCuts(basePlotter.sanityCheck, basePlotter.dict_cat_cut[flavour])

plots = basePlotter.generatePlots(categories, stage, systematic="nominal", weights=[], requested_plots=plots_for_branches)

def plots_to_branches(plots, tree):
    for plot in plots:
        # Ignore 2D plots
        if ":::" in plot["variable"]:
            continue

        branch = {}
        branch["name"] = plot["name"].split("_"+flavour)[0]
        branch["variable"] = plot["variable"]
        if "type" in plot:
            branch["type"] = plot["type"]

        tree["branches"].append(branch)

plots_to_branches(plots, tree)
