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


include_directories = []
plots = []
library_directories = []
libraries = []

code_before_loop = default_code_before_loop()
code_in_loop = default_code_in_loop()
code_after_loop = default_code_after_loop()
headers = default_headers()

include_directories.append(os.path.join(scriptDir, "..", "common"))

# Plot configuration

# lljj 
weights_lljj = ['trigeff', 'llidiso', 'pu']
categories_lljj = ["All", "MuMu", "ElEl", "MuEl"] 
plots_lljj = ["mll", "mjj", "basic", "cmva", "bdtinput", "evt", "dy_bdt_inputs", "dy_rwgt_bdt"]
#categories_lljj = ["All"] 
#plots_lljj = ["dy_rwgt_bdt", "dy_rwgt_bdt_flavour"]

# Weights
# plots_lljj += ["llidisoWeight", "trigeffWeight", "puWeight"]

#llbb
# weights_llbb = ['trigeff', 'llidiso', 'pu', 'jjbtag_heavy', 'jjbtag_light']

# FIXME: We don't have cMVAv2 SFs yet, so do not include b-tagging SFs
weights_llbb = ['trigeff', 'llidiso', 'pu']
categories_llbb = ["All", "MuMu", "ElEl", "MuEl"] 
plots_llbb = plots_lljj + ["resonant_nnoutput", "nonresonant_nnoutput"]

# No systematics
systematics = {"modifObjects" : ["nominal"]}
# All systematics
#systematics = {"modifObjects" : ["nominal", "jecup", "jecdown", "jerup", "jerdown"], "SF" : ["elidisoup", "elidisodown", "muidup", "muiddown", "muisoup", "muisodown", "jjbtagup", "jjbtagdown", "puup", "pudown", "trigeffup", "trigeffdown", "pdfup", "pdfdown", "scale", "scaleUncorr"]}
# No b-tag SF systematics AND NO JEC/JER FOR NOW
#systematics = { "modifObjects": ["nominal"], "SF": ["elidisoup", "elidisodown", "muidup", "muiddown", "muisoup", "muisodown", "puup", "pudown", "trigeffup", "trigeffdown", "pdfup", "pdfdown", "scale", "scaleUncorr"] }

## Define binning of 2D templates for fitting
#chosen2Dbinnings = {
#        "3x25": {
#            "mjjBinning": "3, { 0, 75, 140, 13000 }",
#            "bdtNbins": 25
#        },
#    }

for systematicType in systematics.keys():
    
    for systematic in systematics[systematicType]:
        if systematicType == "modifObjects":
            objects = systematic
        else:
            objects = "nominal" #ensure that we use normal hh_objects for systematics not modifying obect such as scale factors 

        ## lljj 
        basePlotter_lljj = BasePlotter(baseObjectName = "hh_llmetjj_HWWleptons_nobtag_cmva", btagWP_str = 'nobtag', objects = objects)
        
        plots.extend(basePlotter_lljj.generatePlots(categories_lljj, "no_cut", systematic = systematic, weights = weights_lljj, requested_plots = plots_lljj))
        plots.extend(basePlotter_lljj.generatePlots(categories_lljj, "mll_cut", systematic = systematic, weights = weights_lljj, requested_plots = plots_lljj))
        plots.extend(basePlotter_lljj.generatePlots(categories_lljj, "inverted_mll_cut", systematic = systematic, weights = weights_lljj, requested_plots = plots_lljj))

        # no btag -> btagM reweighting applied
        plots.extend(basePlotter_lljj.generatePlots(categories_lljj, "no_cut", systematic=systematic, weights=weights_lljj + ['dy_nobtag_to_btagM_BDT'], requested_plots=plots_llbb + ['DYNobtagToBTagMWeight'], extraString='_with_nobtag_to_btagM_reweighting', allowWeightedData=True))
        plots.extend(basePlotter_lljj.generatePlots(categories_lljj, "mll_cut", systematic=systematic, weights=weights_lljj + ['dy_nobtag_to_btagM_BDT'], requested_plots=plots_llbb + ['DYNobtagToBTagMWeight'], extraString='_with_nobtag_to_btagM_reweighting', allowWeightedData=True))
        plots.extend(basePlotter_lljj.generatePlots(categories_lljj, "inverted_mll_cut", systematic = systematic, weights = weights_lljj + ['dy_nobtag_to_btagM_BDT'], requested_plots = plots_llbb + ['DYNobtagToBTagMWeight'], extraString='_with_nobtag_to_btagM_reweighting', allowWeightedData=True))

        code_in_loop += basePlotter_lljj.get_code_in_loop()
        code_before_loop += basePlotter_lljj.get_code_before_loop()
        code_after_loop += basePlotter_lljj.get_code_after_loop()
        
        # llbb 
        basePlotter_llbb = BasePlotter(baseObjectName = "hh_llmetjj_HWWleptons_btagM_cmva", btagWP_str = 'medium', objects = objects)
       
        plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "no_cut", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
        plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "mll_cut", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
        plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "inverted_mll_cut", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))

        # if systematic == 'nominal':
            # plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "mll_cut", systematic = systematic, weights = weights_llbb, requested_plots = ["llidisoWeight", ], fit2DtemplatesBinning = chosen2Dbinnings))
        
        ## With mll cut + actually cut into mjj sidebands
        #plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "mjj_blind", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
        #plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "mjj_blind", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        
        ## With mll cut + select into high-BDT regions
        #plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "highBDT_node_SM", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
        #plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "highBDT_node_2", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))

        code_in_loop += basePlotter_llbb.get_code_in_loop()
        code_before_loop += basePlotter_llbb.get_code_before_loop()
        code_after_loop += basePlotter_llbb.get_code_after_loop()
