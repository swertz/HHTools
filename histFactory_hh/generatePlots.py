import ROOT as R
import copy, sys, os, inspect 

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import *
from HHAnalysis import HH

includes = []
plots = []
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
    node_str = str(node)
    sample_weights[ "cluster_" + node_str ] = "getBenchmarkReweighter().getWeight({}-1, hh_gen_mHH, hh_gen_costhetastar)".format(node)

# Plot configuration

# lljj 
weights_lljj = ['trigeff', 'llidiso', 'pu']
categories_lljj = ["All"] 
stage_lljj = "no_cut"
plots_lljj = ["mll", "mjj", "basic", "csv", "bdtinput"]

#llbb
weights_llbb = ['trigeff', 'llidiso', 'pu', 'jjbtag']
categories_llbb = ["All"]
stage_llbb = "no_cut"
plots_llbb = plots_lljj
#plots_llbb = ["bdtinput", "mjj"]

systematics = {"modifObjects" : ["nominal"]}
#systematics = {"modifObjects" : ["nominal", "jecup", "jecdown", "jerup", "jerdown"], "SF" : ["elidisoup", "elidisodown", "muidup", "muiddown", "muisoup", "muisodown", "jjbtagup", "jjbtagdown", "puup", "pudown", "trigeffup", "trigeffdown", "pdfup", "pdfdown", "scale"]}
extraSys = []

for systematicType in systematics.keys() :
    
    for systematic in systematics[systematicType]:
        if systematicType == "modifObjects" :
            objects = systematic
        else : 
            objects = "nominal" #ensure that we use normal hh_objects for systematics not modifying obect such as scale factors 

        ## lljj 
        basePlotter = BasePlotter(baseObjectName = "hh_llmetjj_HWWleptons_nobtag_csv", btagWP_str = 'nobtag', objects = objects)
        plots.extend(basePlotter.generatePlots(categories_lljj, stage_lljj, systematic = systematic, weights = weights_lljj, requested_plots = plots_lljj))
        ##plots.extend(basePlotter.generatePlots(categories_lljj, stage_lljj, systematic = systematic, weights = weights_lljj, requested_plots = plots_lljj))
 
        ## llbb 
        basePlotter = BasePlotter(baseObjectName = "hh_llmetjj_HWWleptons_btagM_csv", btagWP_str = 'medium', objects = objects)
        plots.extend(basePlotter.generatePlots(categories_llbb, stage_llbb, systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
        plots.extend(basePlotter.generatePlots(categories_llbb, "mll_cut", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
        plots.extend(basePlotter.generatePlots(categories_llbb, "mll_cut", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))


objects = "nominal"
systematic = "nominal"
## Plots for ht and n vertex
#basePlotter = BasePlotter(baseObjectName = "hh_llmetjj_HWWleptons_nobtag_csv", btagWP_str = 'nobtag', objects = 'nominal')
#plots.extend(basePlotter.generatePlots(categories_lljj, stage_lljj, systematic = "nominal", weights = ['trigeff', 'llidiso', 'pu'], requested_plots = ["vertex"]))
#plots.extend(basePlotter.generatePlots(categories_lljj, stage_lljj, systematic = "nominal", weights = ['trigeff', 'llidiso'], requested_plots = ["vertex"], extraString = "_noPuWeight"))
#plots.extend(basePlotter.generatePlots(categories_lljj, stage_lljj, systematic = "nominal", weights = [], requested_plots = ["ht"]))
## gen content for DY
#plots.extend(basePlotter.generatePlots(categories_lljj, stage_lljj, systematic = "nominal", weights = ['trigeff', 'llidiso', 'pu'], requested_plots = ["flavour"]))
for systematic in extraSys : #does not need modify objects
    # Plots in the four regions for limits
    basePlotter = BasePlotter(baseObjectName = baseObjectName_llbb, btagWP_str = 'medium', objects = objects)
    plots.extend(basePlotter.generatePlots(categories_llbb, "lowBDT_mjjP_400", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
    plots.extend(basePlotter.generatePlots(categories_llbb, "lowBDT_mjjP_650", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
    plots.extend(basePlotter.generatePlots(categories_llbb, "lowBDT_mjjSB_400", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
    plots.extend(basePlotter.generatePlots(categories_llbb, "lowBDT_mjjSB_650", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
    plots.extend(basePlotter.generatePlots(categories_llbb, "highBDT_mjjP_400", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
    plots.extend(basePlotter.generatePlots(categories_llbb, "highBDT_mjjP_650", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
    plots.extend(basePlotter.generatePlots(categories_llbb, "highBDT_mjjSB_400", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
    plots.extend(basePlotter.generatePlots(categories_llbb, "highBDT_mjjSB_650", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
