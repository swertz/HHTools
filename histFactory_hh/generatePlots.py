import ROOT as R
import copy, sys, os, inspect 

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import *
from HHAnalysis import HH
includes = ["/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/HHTools/histFactory_hh/readMVA.h"]

plots = []

## lljj 
#basePlotter = BasePlotter(mode = "custom", baseObjectName = "hh_llmetjj_HWWleptons_nobtag_csv", btagWP_str = 'nobtag', objects = "nominal")
#weights_lljj = ['trigeff', 'llidiso', 'pu']
#categories_lljj = ["ElEl", "MuMu", "MuEl"]
#stage_lljj = "no_cut"
#plots_lljj = ["mll", "basic", "csv"]
#plots.extend(basePlotter.generatePlots(categories_lljj, stage_lljj, systematic = "nominal", weights = weights_lljj, requested_plots = plots_lljj))

# llbb 
basePlotter = BasePlotter(mode = "custom", baseObjectName = "hh_llmetjj_HWWleptons_btagM_csv", btagWP_str = 'medium', objects = "nominal")
weights_llbb = ['trigeff', 'llidiso', 'pu', 'jjbtag']
categories_llbb = ["All"]
stage_llbb = "no_cut"
plots_llbb = ["mjj", "basic", "bdtinput"]
plots.extend(basePlotter.generatePlots(categories_llbb, stage_llbb, systematic = "nominal", weights = weights_llbb, requested_plots = plots_llbb))
plots.extend(basePlotter.generatePlots(categories_llbb, "nminusonedrll_cut", systematic = "nominal", weights = weights_llbb, requested_plots = ["cleancut"]))
plots.extend(basePlotter.generatePlots(categories_llbb, "nminusonedrjj_cut", systematic = "nominal", weights = weights_llbb, requested_plots = ["cleancut"]))
plots.extend(basePlotter.generatePlots(categories_llbb, "nminusonedphilljj_cut", systematic = "nominal", weights = weights_llbb, requested_plots = ["cleancut"]))

# llbb after cleaning 
baseObjectName_llbb = "hh_llmetjj_HWWleptons_btagM_csv"
basePlotter = BasePlotter(mode = "custom", baseObjectName = baseObjectName_llbb, btagWP_str = 'medium', objects = "nominal")
categories_llbb_clean = ["All"]
stage_llbb_clean = "cleaning_cut"
plots.extend(basePlotter.generatePlots(categories_llbb_clean, stage_llbb_clean, systematic = "nominal", weights = weights_llbb, requested_plots = ["bdtinput"]))

# Plots with systematics
systematics = {"modifObjects" : ["nominal", "jecup", "jecdown", "jerup", "jerdown"], "SF" : ["elidisoup", "elidisodown", "muidisoup", "muidisodown", "jjbtagup", "jjbtagdown", "puup", "pudown", "trigeffup", "trigeffdown"]}
for systematicType in systematics.keys() :
    for systematic in systematics[systematicType]:
        if systematicType == "modifObjects" :
            objects = systematic
        else : 
            objects = "nominal" #ensure that we use normal hh_objects for systematics not modifying obect such as scale factors 
        basePlotter = BasePlotter(mode = "custom", baseObjectName = baseObjectName_llbb, btagWP_str = 'medium', objects = objects)
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, stage_llbb_clean, systematic = systematic, weights = weights_llbb, requested_plots = ["mjj", "bdtoutput", "isElEl"]))# "llidisoWeight", 'jjbtagWeight', 'trigeffWeight', 'puWeight']))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "region_1_400", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "region_1_650", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "region_4_400", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "region_4_650", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
        # lljj 
        basePlotter = BasePlotter(mode = "custom", baseObjectName = "hh_llmetjj_HWWleptons_nobtag_csv", btagWP_str = 'nobtag', objects = "nominal")
        weights_lljj = ['trigeff', 'llidiso', 'pu']
        categories_lljj = ["ElEl", "MuMu", "MuEl"]
        stage_lljj = "no_cut"
        plots_lljj = ["mll", "basic", "csv"]
        plots.extend(basePlotter.generatePlots(categories_lljj, stage_lljj, systematic = "nominal", weights = weights_lljj, requested_plots = plots_lljj))

# Plots to control bdt output 
basePlotter = BasePlotter(mode = "custom", baseObjectName = baseObjectName_llbb, btagWP_str = 'medium', objects = "nominal")
plots.extend(basePlotter.generatePlots(categories_llbb_clean, "region_3_400", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
plots.extend(basePlotter.generatePlots(categories_llbb_clean, "region_3_650", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
plots.extend(basePlotter.generatePlots(categories_llbb_clean, "region_4_400", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
plots.extend(basePlotter.generatePlots(categories_llbb_clean, "region_4_650", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
plots.extend(basePlotter.generatePlots(categories_llbb_clean, "region_3and4_400", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
plots.extend(basePlotter.generatePlots(categories_llbb_clean, "region_3and4_650", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
plots.extend(basePlotter.generatePlots(categories_llbb_clean, "region_2and4_400", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
plots.extend(basePlotter.generatePlots(categories_llbb_clean, "region_2and4_650", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
# Plots to control mjj 
plots.extend(basePlotter.generatePlots(categories_llbb_clean, "region_3and4_400", systematic = systematic, weights = weights_llbb, requested_plots = ["mjj"]))
plots.extend(basePlotter.generatePlots(categories_llbb_clean, "region_3and4_650", systematic = systematic, weights = weights_llbb, requested_plots = ["mjj"]))
