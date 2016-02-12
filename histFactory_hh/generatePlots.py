import ROOT as R
import copy, sys, os, inspect 

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import *
from HHAnalysis import HH
includes = ["/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/HHTools/histFactory_hh/readMVA.h"]

plots = []

weights_llbb = ['trigeff', 'llidiso', 'pu', 'jjbtag']
categories_llbb = ["All"]
stage_llbb = "no_cut"
plots_llbb = ["mjj", "basic", "bdtinput"]

categories_llbb_clean = ["All"]
baseObjectName_llbb = "hh_llmetjj_HWWleptons_btagM_csv"
stage_llbb_clean = "cleaning_cut"

systematics = {"modifObjects" : ["nominal", "jecup", "jecdown", "jerup", "jerdown"], "SF" : ["elidisoup", "elidisodown", "muidisoup", "muidisodown", "jjbtagup", "jjbtagdown", "puup", "pudown", "trigeffup", "trigeffdown"]}
for systematicType in systematics.keys() :
    for systematic in systematics[systematicType]:
        if systematicType == "modifObjects" :
            objects = systematic
        else : 
            objects = "nominal" #ensure that we use normal hh_objects for systematics not modifying obect such as scale factors 

        # lljj 
        basePlotter = BasePlotter(mode = "custom", baseObjectName = "hh_llmetjj_HWWleptons_nobtag_csv", btagWP_str = 'nobtag', objects = objects)
        weights_lljj = ['trigeff', 'llidiso', 'pu']
        categories_lljj = ["ElEl", "MuMu", "MuEl"]
        stage_lljj = "no_cut"
        plots_lljj = ["mll", "basic", "csv"]
        plots.extend(basePlotter.generatePlots(categories_lljj, stage_lljj, systematic = systematic, weights = weights_lljj, requested_plots = plots_lljj))
        
        # llbb 
        basePlotter = BasePlotter(mode = "custom", baseObjectName = "hh_llmetjj_HWWleptons_btagM_csv", btagWP_str = 'medium', objects = objects)
        plots.extend(basePlotter.generatePlots(categories_llbb, stage_llbb, systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
        plots.extend(basePlotter.generatePlots(categories_llbb, "nminusonedrll_cut", systematic = systematic, weights = weights_llbb, requested_plots = ["cleancut"]))
        plots.extend(basePlotter.generatePlots(categories_llbb, "nminusonedrjj_cut", systematic = systematic, weights = weights_llbb, requested_plots = ["cleancut"]))
        plots.extend(basePlotter.generatePlots(categories_llbb, "nminusonedphilljj_cut", systematic = systematic, weights = weights_llbb, requested_plots = ["cleancut"]))
       
        # llbb after pre-selection
        basePlotter = BasePlotter(mode = "custom", baseObjectName = baseObjectName_llbb, btagWP_str = 'medium', objects = objects)
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, stage_llbb_clean, systematic = systematic, weights = weights_llbb, requested_plots = ["mjj", "bdtinput", "bdtoutput", "isElEl"]))# "llidisoWeight", 'jjbtagWeight', 'trigeffWeight', 'puWeight']))

        # Plots for yields
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "highBDT_mjjP_400", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "highBDT_mjjP_650", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "lowBDT_mjjSB_400", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "lowBDT_mjjSB_650", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
        
        # Plots to control bdt output 
        basePlotter = BasePlotter(mode = "custom", baseObjectName = baseObjectName_llbb, btagWP_str = 'medium', objects = objects)
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "lowBDT_mjjP_400", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "lowBDT_mjjP_650", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "lowBDT_mjjSB_400", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "lowBDT_mjjSB_650", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "lowBDT_mjjall_400", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "lowBDT_mjjall_650", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "allBDT_mjjSB_400", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "allBDT_mjjSB_650", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        
        # Plots to control mjj 
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "lowBDT_mjjall_400", systematic = systematic, weights = weights_llbb, requested_plots = ["mjj"]))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "lowBDT_mjjall_650", systematic = systematic, weights = weights_llbb, requested_plots = ["mjj"]))

#for plot in plots : 
#    print plot["name"]

