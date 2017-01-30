import copy, sys, os, inspect, yaml

scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import *

###### Old Reweighting -- template-based #########
#sample_weights = {}

#headers.append("reweight_v1tov3.h")

## For v1->v3 reweighting
#code_before_loop += """
#getBenchmarkReweighter("/home/fynu/sbrochet/scratch/Framework/CMSSW_7_6_5/src/cp3_llbb/HHTools/scripts/", 0, 11, true, "cluster_NUM_v1_to_v3_weights.root", "NUM");
#"""
#for node in range(1, 13):
#    sample_weights[ "cluster_node_" + str(node) ] = "getBenchmarkReweighter().getWeight({}-1, hh_gen_mHH, hh_gen_costhetastar)".format(node)

## For v1->1507 reweighting
#code_before_loop += """
#getBenchmarkReweighter("/home/fynu/swertz/scratch/CMSSW_7_6_3_patch2/src/cp3_llbb/HHTools/scripts/weights_v1_1507_points.root", 0, 1506, false, "point_NUM_weights_unfolded", "NUM");
#"""
#for node in range(0, 1507):
#    if node in [324, 910, 985, 990]: continue # Skip dummy Xanda
#    sample_weights[ "point_" + str(node) ] = "getBenchmarkReweighter().getWeight({}, hh_gen_mHH, hh_gen_costhetastar)".format(node)

## For v1->v1 checks:
#code_before_loop += """
#getBenchmarkReweighter("/home/fynu/swertz/scratch/CMSSW_7_6_3_patch2/src/cp3_llbb/HHTools/scripts/", 2, 13, true, "cluster_NUM_v1_to_v3_weights.root", "NUM");
#"""
#for node in range(2, 14):
#    sample_weights[ "cluster_node_rwgt_" + str(node) ] = "getBenchmarkReweighter().getWeight({}, hh_gen_mHH, hh_gen_costhetastar)".format(node)

### BM to MV term reweighting
##operators_MV = ["OtG", "Otphi", "O6", "OH"]
##rwgt_base = [ "SM", "box" ] + range(2, 13)
##for base, base_name in enumerate(rwgt_base):
##    for i, op1 in enumerate(operators_MV):
##        sample_weights["base_" + base_name + "_SM_" + op1] = "getHHEFTReweighter().getMVTermME(hh_gen_H1, hh_gen_H2, -1, {}, event_alpha_QCD)/getHHEFTReweighter().getBenchmarkME(hh_gen_H1, hh_gen_H2, {}, event_alpha_QCD)".format(i, base)
##        for j, op2 in enumerate(operators_MV):
##            if i < j: continue
##            sample_weights["base_" + base_name + "_" + op1 + "_" + op2] = "getHHEFTReweighter().getMVTermME(hh_gen_H1, hh_gen_H2, {}, {}, event_alpha_QCD)/getHHEFTReweighter().getBenchmarkME(hh_gen_H1, hh_gen_H2, {}, event_alpha_QCD)".format(i, j, base)

##### Some helper functions #####

def check_overlap(lst):
    if not any(lst) or sum(lst) != 1:
        raise Exception("Arguments passed to generatePlots.py are not consistent!")

def getBinningStrWithMax(nBins, start, end, max):
    """Return string defining a binning in histFactory, with 'nBins' bins between
    'start' and 'end', but with the upper edge replaced by 'max'."""
    
    bins = [start]
    pos = start
    for i in range(nBins):
        pos += (end-start)/nBins
        bins.append(pos)
    if bins[-1] < max:
        bins[-1] = max

    m_string = str(len(bins)-1) + ", { "
    for b in bins[0:len(bins)-1]:
        m_string += str(b) + ", "
    m_string += str(bins[-1]) + "}"

    return m_string

##### Retrieve config file written by launchHistFactory.py:
config = {}
with open(os.path.join("/tmp", os.getenv("USER") + "_factory.json")) as f:
    # Use YAML because JSON loads strings as unicode by default, and this messes with Factories
    config = yaml.safe_load(f)

def get_cfg(var, default=False):
    if var in config.keys():
        return config[var]
    else:
        return default

for_data = (config['sample_type'] == 'Data')
for_MC = (config['sample_type'] == 'MC')
for_signal = (config['sample_type'] == 'Signal')
check_overlap([for_data, for_MC, for_signal])

use_syst = get_cfg('syst')

lljj_categories = get_cfg('lljj_categories', ['MuMu', 'MuEl', 'ElEl'])
llbb_categories = get_cfg('llbb_categories', ['MuMu', 'MuEl', 'ElEl'])
lljj_stages = get_cfg('lljj_stages', ['no_cut', 'mll_cut', 'inverted_mll_cut'])
llbb_stages = get_cfg('llbb_stages', ['no_cut', 'mll_cut', 'inverted_mll_cut'])
lljj_plot_families = get_cfg('lljj_plots', [])
llbb_plot_families = get_cfg('llbb_plots', [])

# Ask Factories to regroup "similar" plots
# Don't it for data (not supported by Factories to use weighted data)
if not for_data:
    optimize_plots = True

####### Configure additional content for factory ####
plots = []
library_directories = []
sample_weights = {}

code_before_loop = default_code_before_loop()
code_in_loop = default_code_in_loop()
code_after_loop = default_code_after_loop()
include_directories = default_include_directories(scriptDir)
headers = default_headers()
libraries = default_libraries()
sources = default_sources(scriptDir)

####### Reweighting -- ME-based -- only for signal #########
if for_signal:
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

#### lljj 
weights_lljj = ['trigeff', 'llidiso', 'pu']

plots_lljj = []
if "basic" in lljj_plot_families:
    plots_lljj += ["mjj", "basic", "cmva", "nn_inputs", "evt", "dy_bdt_inputs"]
if "dy_bdt" in lljj_plot_families:
    plots_lljj += ["dy_rwgt_bdt"]
if "dy_bdt_flavour" in lljj_plot_families:
    plots_lljj += ["dy_rwgt_bdt_flavour"]
if "weights" in lljj_plot_families:
    plots_lljj += ["llidisoWeight", "trigeffWeight", "puWeight", "DYNobtagToBTagMWeight"]

#### llbb
weights_llbb = ['trigeff', 'llidiso', 'pu', 'jjbtag_heavy', 'jjbtag_light']

plots_llbb = []
if "basic" in llbb_plot_families:
    plots_llbb += ["mjj", "basic", "cmva", "nn_inputs", "evt", "dy_bdt_inputs"]
if "dy_bdt" in llbb_plot_families:
    plots_llbb += ["dy_rwgt_bdt"]
if "nn" in llbb_plot_families:
    plots_llbb += ["resonant_nnoutput", "nonresonant_nnoutput"]
if "mjj_vs_nn" in llbb_plot_families:
    plots_llbb += ["mjj_vs_resonant_nnoutput", "mjj_vs_nonresonant_nnoutput"]
if "weights" in llbb_plot_families:
    plots_llbb += ["llidisoWeight", "trigeffWeight", "puWeight", "jjbtagWeight", "DYNobtagToBTagMWeight"]

# No weights for data!
if for_data:
    weights_lljj = []
    weights_llbb = []

##### Systematics ####
if not use_syst:
    # No systematics
    systematics = { "modifObjects": ["nominal"] }
else:
    # All systematics
    systematics = { 
            "modifObjects": [
                "nominal",
                "jecup", "jecdown",
                "jerup", "jerdown"
                ], 
            "SF": [
                "elidisoup", "elidisodown",
                "muidup", "muiddown",
                "muisoup", "muisodown",
                "jjbtaglightup", "jjbtaglightdown",
                "jjbtagheavyup", "jjbtagheavydown",
                "puup", "pudown",
                "trigeffup", "trigeffdown",
                "pdfup", "pdfdown",
                "dyStatup", "dyStatdown"
                ]
            }
    
    # Scale uncertainties: depends on what we're running on
    for i in range(6):
        if not for_data:
            systematics["SF"].append("scaleUncorr{}".format(i))
        if not for_signal:
            systematics["SF"].append("dyScaleUncorr{}".format(i))

#### Generate plot list #####
for systematicType in systematics.keys():
    
    for systematic in systematics[systematicType]:
        if systematicType == "modifObjects" and not for_data:
            objects = systematic
        else:
            objects = "nominal" #ensure that we use normal hh_objects for systematics not modifying obect such as scale factors 


        ###### llbb stage ######
        if "dyStat" not in systematic and "dyScale" not in systematic:
            basePlotter_llbb = BasePlotter(baseObjectName = "hh_llmetjj_HWWleptons_btagM_cmva", btagWP_str = 'medium', objects = objects)
 
        for stage in llbb_stages:
            plots.extend(basePlotter_llbb.generatePlots(llbb_categories, stage, systematic=systematic, weights=weights_llbb, requested_plots=plots_llbb))

        # Signal: only do llbb!
        if for_signal:
            continue


        ##### lljj stage ###### 
        basePlotter_lljj = BasePlotter(baseObjectName = "hh_llmetjj_HWWleptons_nobtag_cmva", btagWP_str = 'nobtag', objects = objects)
        
        if "dyStat" not in systematic and "dyScale" not in systematic and "jjbtag" not in systematic:
            for stage in lljj_stages:
                plots.extend(basePlotter_lljj.generatePlots(lljj_categories, stage, systematic=systematic, weights=weights_lljj, requested_plots=plots_lljj))


        ###### lljj stage + no btag -> btagM reweighting applied: use LLBB values! #####
        for stage in llbb_stages:
            plots.extend(basePlotter_lljj.generatePlots(llbb_categories, stage, systematic=systematic, weights=weights_lljj + ['dy_nobtag_to_btagM_BDT'], requested_plots=plots_llbb, extraString='_with_nobtag_to_btagM_reweighting'))
        

extra_branches = [
        # Needed for the computation of HT,
        # In case the branches are not already read
        "hh_jets",
        "hh_leptons",
    ]

