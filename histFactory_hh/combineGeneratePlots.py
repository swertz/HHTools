import ROOT as R
import copy, sys, os, inspect 

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import *
from HHAnalysis import HH
includes = ["/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/HHTools/histFactory_hh/readMVA.h"]

plots = []

# Plots to feed combine
baseObjectName = "hh_llmetjj_HWWleptons_btagM_csv"
weights = ['trigeff', 'llidiso', 'pu', 'jjbtag']
categories = ["All"] #, "ElEl", "MuMu", "MuEl"]
systematics = {"modifObjects" : ["nominal", "jecup", "jecdown", "jerup", "jerdown"], "SF" : ["elidisoup", "elidisodown", "muidisoup", "muidisodown", "jjbtagup", "jjbtagdown", "puup", "pudown", "trigeffup", "trigeffdown"]}
for systematicType in systematics.keys() :
    for systematic in systematics[systematicType]:
        if systematicType == "modifObjects" :
            objects = systematic
        else : 
            objects = "nominal" # ensures that we use normal hh_objects for systematics not modifying obect such as scale factors 
        basePlotter = BasePlotter(mode = "custom", baseObjectName = baseObjectName, btagWP_str = 'medium', objects = objects)
        plots.extend(basePlotter.generatePlots(categories, "region_1_400", systematic = systematic, weights = weights, requested_plots = ["mjj", "bdtoutput"]))
        plots.extend(basePlotter.generatePlots(categories, "region_1_650", systematic = systematic, weights = weights, requested_plots = ["mjj", "bdtoutput"]))
        plots.extend(basePlotter.generatePlots(categories, "region_2_400", systematic = systematic, weights = weights, requested_plots = ["mjj", "bdtoutput"]))
        plots.extend(basePlotter.generatePlots(categories, "region_2_650", systematic = systematic, weights = weights, requested_plots = ["mjj", "bdtoutput"]))
        plots.extend(basePlotter.generatePlots(categories, "region_3_400", systematic = systematic, weights = weights, requested_plots = ["mjj", "bdtoutput"]))
        plots.extend(basePlotter.generatePlots(categories, "region_3_650", systematic = systematic, weights = weights, requested_plots = ["mjj", "bdtoutput"]))
        plots.extend(basePlotter.generatePlots(categories, "region_4_400", systematic = systematic, weights = weights, requested_plots = ["mjj", "bdtoutput"]))
        plots.extend(basePlotter.generatePlots(categories, "region_4_650", systematic = systematic, weights = weights, requested_plots = ["mjj", "bdtoutput"]))
