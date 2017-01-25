import ROOT as R
import copy, sys, os, inspect 

scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import *
from HHAnalysis import HH

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


plots = []
library_directories = []

code_before_loop = default_code_before_loop()
code_in_loop = default_code_in_loop()
code_after_loop = default_code_after_loop()
include_directories = default_include_directories(scriptDir)
headers = default_headers()
libraries = default_libraries()
sources = default_sources(scriptDir)

# Plot configuration

# lljj 
weights_lljj = ['trigeff', 'llidiso', 'pu']
categories_lljj = ["All", "MuMu", "ElEl", "MuEl"] 
plots_lljj = ["mll", "mjj", "basic", "cmva", "bdtinput", "evt", "dy_bdt_inputs", "dy_rwgt_bdt"]
#categories_lljj = ["SF"] 
#plots_lljj = ["dy_rwgt_bdt", "dy_rwgt_bdt_flavour"]

# Weights
# plots_lljj += ["llidisoWeight", "trigeffWeight", "puWeight"]

#llbb
weights_llbb = ['trigeff', 'llidiso', 'pu', 'jjbtag_heavy', 'jjbtag_light']
categories_llbb = ["MuMu", "ElEl", "MuEl"] 
plots_llbb = plots_lljj + ["resonant_nnoutput", "nonresonant_nnoutput"]

# No systematics
#systematics = { "modifObjects": ["nominal"] }
# All systematics
systematics = { "modifObjects": ["nominal", "jecup", "jecdown", "jerup", "jerdown"], "SF": ["elidisoup", "elidisodown", "muidup", "muiddown", "muisoup", "muisodown", "jjbtaglightup", "jjbtaglightdown", "jjbtagheavyup", "jjbtagheavydown", "puup", "pudown", "trigeffup", "trigeffdown", "pdfup", "pdfdown", "dyStatup", "dyStatdown"] }
for i in range(6):
    systematics["SF"].append("scaleUncorr{}".format(i))

for systematicType in systematics.keys():
    
    for systematic in systematics[systematicType]:
        if systematicType == "modifObjects":
            objects = systematic
        else:
            objects = "nominal" #ensure that we use normal hh_objects for systematics not modifying obect such as scale factors 

        # lljj 
        basePlotter_lljj = BasePlotter(baseObjectName = "hh_llmetjj_HWWleptons_nobtag_cmva", btagWP_str = 'nobtag', objects = objects)
        
        if "dyStat" not in systematic and "jjbtag" not in systematics:
            plots.extend(basePlotter_lljj.generatePlots(categories_lljj, "no_cut", systematic = systematic, weights = weights_lljj, requested_plots = plots_lljj))
            plots.extend(basePlotter_lljj.generatePlots(categories_lljj, "mll_cut", systematic = systematic, weights = weights_lljj, requested_plots = plots_lljj))
            plots.extend(basePlotter_lljj.generatePlots(categories_lljj, "inverted_mll_cut", systematic = systematic, weights = weights_lljj, requested_plots = plots_lljj))

        # lljj, with no btag -> btagM reweighting applied
        plots.extend(basePlotter_lljj.generatePlots(categories_llbb, "no_cut", systematic=systematic, weights=weights_lljj + ['dy_nobtag_to_btagM_BDT'], requested_plots=plots_llbb, extraString='_with_nobtag_to_btagM_reweighting', allowWeightedData=True))
        plots.extend(basePlotter_lljj.generatePlots(categories_llbb, "mll_cut", systematic=systematic, weights=weights_lljj + ['dy_nobtag_to_btagM_BDT'], requested_plots=plots_llbb, extraString='_with_nobtag_to_btagM_reweighting', allowWeightedData=True))
        plots.extend(basePlotter_lljj.generatePlots(categories_llbb, "inverted_mll_cut", systematic = systematic, weights = weights_lljj + ['dy_nobtag_to_btagM_BDT'], requested_plots = plots_llbb, extraString='_with_nobtag_to_btagM_reweighting', allowWeightedData=True))
        
        # llbb 
        if "dyStat" not in systematic:
            basePlotter_llbb = BasePlotter(baseObjectName = "hh_llmetjj_HWWleptons_btagM_cmva", btagWP_str = 'medium', objects = objects)
           
            plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "no_cut", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
            plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "mll_cut", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
            plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "inverted_mll_cut", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
