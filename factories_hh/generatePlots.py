import copy, sys, os, inspect, yaml

scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import *

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
syst_split_jec = get_cfg('syst_split_jec', False)
syst_only_jec = get_cfg('syst_only_jec', False)
syst_split_pdf = get_cfg('syst_split_pdf', False)

lljj_categories = get_cfg('lljj_categories', ['MuMu', 'MuEl', 'ElEl'])
llbb_categories = get_cfg('llbb_categories', ['MuMu', 'MuEl', 'ElEl'])
lljj_stages = get_cfg('lljj_stages', ['no_cut', 'mll_cut'])
llbb_stages = get_cfg('llbb_stages', ['no_cut', 'mll_cut'])
lljj_plot_families = get_cfg('lljj_plots', [])
llbb_plot_families = get_cfg('llbb_plots', [])
skim_MuEl_stages = get_cfg('skim_MuEl_stages', False) # MuEl category: do only only "mll_cut" for llbb

resonant_signal_grid = get_cfg('resonant_signal_grid', [])
nonresonant_signal_grid = get_cfg('nonresonant_signal_grid', [])
nonresonant_signal_grid = [ tuple(point) for point in nonresonant_signal_grid ] # For some fucking reason

# Ask Factories to regroup "similar" plots
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
library_directories = default_library_directories()
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
    plots_lljj += ["mjj", "basic", "nn_inputs", "dy_bdt_inputs"]
if "other" in lljj_plot_families:
    plots_lljj += ["other"]
if "dy_bdt" in lljj_plot_families:
    plots_lljj += ["dy_rwgt_bdt"]
if "dy_bdt_flavour" in lljj_plot_families:
    plots_lljj += ["dy_rwgt_bdt_flavour"]
if "btag_efficiencies" in lljj_plot_families:
    plots_lljj += ["btag_efficiency_2d"]
if "weights" in lljj_plot_families:
    plots_lljj += ["llidisoWeight", "trigeffWeight", "puWeight", "DYNobtagToBTagMWeight"]

#### llbb
weights_llbb = ['trigeff', 'llidiso', 'pu', 'jjbtag_heavy', 'jjbtag_light']

plots_llbb = []
if "basic" in llbb_plot_families:
    plots_llbb += ["mjj", "basic", "nn_inputs", "dy_bdt_inputs"]
if "other" in llbb_plot_families:
    plots_llbb += ["other"]
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

split_jec_sources_base = [
        "AbsoluteFlavMap",
        "AbsoluteMPFBias",
        "AbsoluteScale",
        "AbsoluteStat",
        "FlavorQCD",
        "Fragmentation",
        "PileUpDataMC",
        "PileUpPtBB",
        "PileUpPtEC1",
        "PileUpPtEC2",
        "PileUpPtHF",
        "PileUpPtRef",
        "RelativeBal",
        "RelativeFSR",
        "RelativeJEREC1",
        "RelativeJEREC2",
        "RelativeJERHF",
        "RelativePtBB",
        "RelativePtEC1",
        "RelativePtEC2",
        "RelativePtHF",
        "RelativeStatEC",
        "RelativeStatFSR",
        "RelativeStatHF",
        "SinglePionECAL",
        "SinglePionHCAL",
        "TimePtEta"]
split_jec_sources = []
for _s in split_jec_sources_base:
    split_jec_sources.append("jec" + _s.lower() + "up")
    split_jec_sources.append("jec" + _s.lower() + "down")

if not use_syst:
    # No systematics
    systematics = { "modifObjects": ["nominal"] }
else:
    # Main systematics
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
                #"elrecoup", "elrecodown",
                #"mutrackingup", "mutrackingdown",
                #"hdampup", "hdampdown",
                ]
            }
    # Scale uncertainties
    for i in range(6):
        systematics["SF"].append("scaleUncorr{}".format(i))
        systematics["SF"].append("dyScaleUncorr{}".format(i))

    # All JEC sources, if asked
    if syst_split_jec:
        systematics["modifObjects"] += split_jec_sources

    # PDF split by initial state, if asked
    if syst_split_pdf:
        for _s in ["qq", "gg", "qg"]:
            systematics["SF"].append("pdf" + _s + "up")
            systematics["SF"].append("pdf" + _s + "down")

    if syst_only_jec:
        systematics["SF"] = []
        systematics["modifObjects"] = split_jec_sources

# Systematic uncertainties: depends on the stage on what we're running on...
def allowed_systematics_llbb(syst):
    if syst == "nominal":
        return True
    if "dyStat" in syst:
        return False
    if "dyScaleUncorr" in syst:
        return False
    if for_data:
        return False
    return True

def allowed_systematics_lljj(syst):
    if syst == "nominal":
        return True
    if "dyStat" in syst:
        return False
    if "dyScaleUncorr" in syst:
        return False
    if "jjbtag" in syst:
        return False
    if for_data:
        return False
    return True

def allowed_systematics_lljj_dy_reweighting(syst):
    if syst == "nominal":
        return True
    # Both MC and Data: only a subset of systematics
    for _s in ["jec", "jer", "jjbtaglight", "jjbtagheavy", "pu", "dyStat", "dyScaleUncorr"]:
        if _s in syst:
            return True
    # MC: also all others
    if for_MC:
        return True
    # Data: nothing else
    return False


#### Generate plot list #####
for systematicType in systematics.keys():
    
    for systematic in systematics[systematicType]:
        if systematicType == "modifObjects" and not for_data:
            objects = systematic
        else:
            objects = "nominal" #ensure that we use normal hh_objects for systematics not modifying obect such as scale factors 


        ###### llbb stage ######
        if allowed_systematics_llbb(systematic):
            
            basePlotter_llbb = BasePlotter(btag=True, objects=objects)
 
            for stage in llbb_stages:
                this_categories = llbb_categories[:]
                if skim_MuEl_stages and stage != "mll_cut" and "MuEl" in this_categories:
                    this_categories.remove("MuEl")
                
                plots.extend(basePlotter_llbb.generatePlots(this_categories, stage, systematic=systematic, weights=weights_llbb, requested_plots=plots_llbb, resonant_signal_grid=resonant_signal_grid, nonresonant_signal_grid=nonresonant_signal_grid, skimSignal2D=for_signal))

        # Signal: only do llbb!
        if for_signal:
            continue


        ##### lljj stage ###### 
        basePlotter_lljj = BasePlotter(btag=False, objects=objects)
        
        if allowed_systematics_lljj(systematic):
 
            for stage in lljj_stages:
                this_categories = lljj_categories[:]
                
                plots.extend(basePlotter_lljj.generatePlots(this_categories, stage, systematic=systematic, weights=weights_lljj, requested_plots=plots_lljj))


        ###### lljj stage + no btag -> btagM reweighting applied: use LLBB values! #####
        if allowed_systematics_lljj_dy_reweighting(systematic):
            
            for stage in llbb_stages:
                this_categories = llbb_categories[:]
                if skim_MuEl_stages and stage != "mll_cut" and "MuEl" in this_categories:
                    this_categories.remove("MuEl")
                
                plots.extend(basePlotter_lljj.generatePlots(this_categories, stage, systematic=systematic, weights=weights_lljj + ['dy_nobtag_to_btagM_BDT'], requested_plots=plots_llbb, extraString='_with_nobtag_to_btagM_reweighting', allowWeightedData=True, resonant_signal_grid=resonant_signal_grid, nonresonant_signal_grid=nonresonant_signal_grid, skimSignal2D=for_signal))
        

#for plot in plots:
#    print plot
