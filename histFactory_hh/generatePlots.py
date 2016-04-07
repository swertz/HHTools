import ROOT as R
import copy, sys, os, inspect 

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import *
from HHAnalysis import HH
includes = ["/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/HHTools/histFactory_hh/readMVA.h"]

plots = []
# lljj 
weights_lljj = ['trigeff', 'llidiso', 'pu']
categories_lljj = ["ElEl", "MuMu", "MuEl"]
stage_lljj = "no_cut"
plots_lljj = ["mll", "basic"]

#llbb
weights_llbb = ['trigeff', 'llidiso', 'pu', 'jjbtag']
categories_llbb = ["All"]
stage_llbb = "no_cut"
plots_llbb = ["mjj", "basic", "cleancut", "isElEl"]

categories_llbb_clean = ["All"]
categories_llbb_combine = ["All", "ElEl", "MuMu", "MuEl"]
baseObjectName_llbb = "hh_llmetjj_HWWleptons_btagM_csv"
stage_llbb_clean = "cleaning_cut"

#systematics = {"modifObjects" : ["nominal"]}
systematics = {"modifObjects" : ["nominal", "jecup", "jecdown", "jerup", "jerdown"], "SF" : ["elidisoup", "elidisodown", "muidup", "muiddown", "muisoup", "muisodown", "jjbtagup", "jjbtagdown", "puup", "pudown", "trigeffup", "trigeffdown", "pdfup", "pdfdown", "scale"]}
extraSys = []
for systematicType in systematics.keys() :
    for systematic in systematics[systematicType]:
        if systematicType == "modifObjects" :
            objects = systematic
        else : 
            objects = "nominal" #ensure that we use normal hh_objects for systematics not modifying obect such as scale factors 

        # lljj 
        basePlotter = BasePlotter(mode = "custom", baseObjectName = "hh_llmetjj_HWWleptons_nobtag_csv", btagWP_str = 'nobtag', objects = objects)
        plots.extend(basePlotter.generatePlots(categories_lljj, stage_lljj, systematic = systematic, weights = weights_lljj, requested_plots = plots_lljj))
        
        # llbb 
        basePlotter = BasePlotter(mode = "custom", baseObjectName = "hh_llmetjj_HWWleptons_btagM_csv", btagWP_str = 'medium', objects = objects)
        plots.extend(basePlotter.generatePlots(["ElEl", "MuEl", "MuMu"], "no_cut", systematic = systematic, weights = weights_llbb, requested_plots = ["mll"]))
        plots.extend(basePlotter.generatePlots(categories_llbb, "nminusonedrll_cut", systematic = systematic, weights = weights_llbb, requested_plots = ["drllcut"]))
        plots.extend(basePlotter.generatePlots(categories_llbb, "nminusonedrjj_cut", systematic = systematic, weights = weights_llbb, requested_plots = ["drjjcut"]))
        plots.extend(basePlotter.generatePlots(categories_llbb, "nminusonedphilljj_cut", systematic = systematic, weights = weights_llbb, requested_plots = ["dphilljjcut"]))
        plots.extend(basePlotter.generatePlots(categories_llbb, "mll_cut", systematic = systematic, weights = weights_llbb, requested_plots = ["cleancut"]))
       
        # llbb after pre-selection
        basePlotter = BasePlotter(mode = "custom", baseObjectName = baseObjectName_llbb, btagWP_str = 'medium', objects = objects)
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, stage_llbb_clean, systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl", "mjj", "basic", "bdtinput", "bdtoutput"]))# "llidisoWeight", 'jjbtagWeight', 'trigeffWeight', 'puWeight']))

#        # Control plots  
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "mjj_cr", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtinput", "bdtoutput"]))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "cr_400_ext", systematic = systematic, weights = weights_llbb, requested_plots = ["mjj", "bdtinput"]))
        plots.extend(basePlotter.generatePlots(categories_llbb_clean, "cr_650_ext", systematic = systematic, weights = weights_llbb, requested_plots = ["mjj", "bdtinput"]))

        # Plots in the four regions
        basePlotter = BasePlotter(mode = "custom", baseObjectName = baseObjectName_llbb, btagWP_str = 'medium', objects = objects)
        plots.extend(basePlotter.generatePlots(categories_llbb, "lowBDT_mjjP_400", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl", "bdtoutput", "mjj", "bdtinput"]))
        plots.extend(basePlotter.generatePlots(categories_llbb, "lowBDT_mjjP_650", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl", "bdtoutput", "mjj", "bdtinput"]))
        plots.extend(basePlotter.generatePlots(categories_llbb, "lowBDT_mjjSB_400", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl", "bdtoutput", "mjj", "bdtinput"]))
        plots.extend(basePlotter.generatePlots(categories_llbb, "lowBDT_mjjSB_650", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl", "bdtoutput", "mjj", "bdtinput"]))
        plots.extend(basePlotter.generatePlots(categories_llbb, "highBDT_mjjP_400", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl", "bdtoutput", "mjj", "bdtinput"]))
        plots.extend(basePlotter.generatePlots(categories_llbb, "highBDT_mjjP_650", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl", "bdtoutput", "mjj", "bdtinput"]))
        plots.extend(basePlotter.generatePlots(categories_llbb, "highBDT_mjjSB_400", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl", "bdtoutput", "mjj", "bdtinput"]))
        plots.extend(basePlotter.generatePlots(categories_llbb, "highBDT_mjjSB_650", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl", "bdtoutput", "mjj", "bdtinput"]))
        # BDT low and high
        plots.extend(basePlotter.generatePlots(categories_llbb, "sr_400_ext", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtinput", "mjj"]))
        plots.extend(basePlotter.generatePlots(categories_llbb, "sr_650_ext", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtinput", "mjj"]))
        plots.extend(basePlotter.generatePlots(categories_llbb, "cr_400_ext", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtinput", "mjj"]))
        plots.extend(basePlotter.generatePlots(categories_llbb, "cr_650_ext", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtinput", "mjj"]))
        #plots.extend(basePlotter.generatePlots(categories_llbb_clean, "lowBDT_mjjall_400", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        #plots.extend(basePlotter.generatePlots(categories_llbb_clean, "lowBDT_mjjall_650", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        #plots.extend(basePlotter.generatePlots(categories_llbb_clean, "highBDT_mjjall_400", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        #plots.extend(basePlotter.generatePlots(categories_llbb_clean, "highBDT_mjjall_650", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        #plots.extend(basePlotter.generatePlots(categories_llbb_clean, "allBDT_mjjSB_400", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        #plots.extend(basePlotter.generatePlots(categories_llbb_clean, "allBDT_mjjSB_650", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        #plots.extend(basePlotter.generatePlots(categories_llbb_clean, "allBDT_mjjP_400", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        #plots.extend(basePlotter.generatePlots(categories_llbb_clean, "allBDT_mjjP_650", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))


objects = "nominal"
systematic = "nominal"
## Plots for ht and n vertex
basePlotter = BasePlotter(mode = "custom", baseObjectName = "hh_llmetjj_HWWleptons_nobtag_csv", btagWP_str = 'nobtag', objects = 'nominal')
plots.extend(basePlotter.generatePlots(categories_lljj, stage_lljj, systematic = "nominal", weights = ['trigeff', 'llidiso', 'pu'], requested_plots = ["vertex"]))
plots.extend(basePlotter.generatePlots(categories_lljj, stage_lljj, systematic = "nominal", weights = ['trigeff', 'llidiso'], requested_plots = ["vertex"], extraString = "_noPuWeight"))
plots.extend(basePlotter.generatePlots(categories_lljj, stage_lljj, systematic = "nominal", weights = [], requested_plots = ["ht"]))
## gen content for DY
plots.extend(basePlotter.generatePlots(categories_lljj, stage_lljj, systematic = "nominal", weights = ['trigeff', 'llidiso', 'pu'], requested_plots = ["flavour"]))
for systematic in extraSys : #does not need modify objects
    # Plots in the four regions for limits
    basePlotter = BasePlotter(mode = "custom", baseObjectName = baseObjectName_llbb, btagWP_str = 'medium', objects = objects)
    plots.extend(basePlotter.generatePlots(categories_llbb, "lowBDT_mjjP_400", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
    plots.extend(basePlotter.generatePlots(categories_llbb, "lowBDT_mjjP_650", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
    plots.extend(basePlotter.generatePlots(categories_llbb, "lowBDT_mjjSB_400", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
    plots.extend(basePlotter.generatePlots(categories_llbb, "lowBDT_mjjSB_650", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
    plots.extend(basePlotter.generatePlots(categories_llbb, "highBDT_mjjP_400", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
    plots.extend(basePlotter.generatePlots(categories_llbb, "highBDT_mjjP_650", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
    plots.extend(basePlotter.generatePlots(categories_llbb, "highBDT_mjjSB_400", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))
    plots.extend(basePlotter.generatePlots(categories_llbb, "highBDT_mjjSB_650", systematic = systematic, weights = weights_llbb, requested_plots = ["isElEl"]))

#for plot in plots : 
#    print plot
#    #print plot["name"]
#    print " "

