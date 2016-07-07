import ROOT as R
import copy, sys, os, inspect 

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
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


includes = []
plots = []
code_before_loop = ""

# Needed to evaluate MVA outputs
includes.append( os.path.join(scriptDir, "..", "common", "readMVA.h") )

# For cluster reweighting
includes.append( os.path.join(scriptDir, "..", "common", "reweight_v1tov3.h") )

code_before_loop += """
getBenchmarkReweighter("/home/fynu/sbrochet/scratch/Framework/CMSSW_7_6_5/src/cp3_llbb/HHTools/scripts/", 0, 11);
"""
## For v1->v1 checks:
#code_before_loop += """
#getBenchmarkReweighter("/home/fynu/swertz/scratch/CMSSW_7_6_3_patch2/src/cp3_llbb/HHTools/scripts/", 2, 13);
#"""

sample_weights = {}
for node in range(1, 13):
    sample_weights[ "cluster_node_" + str(node) ] = "getBenchmarkReweighter().getWeight({}-1, hh_gen_mHH, hh_gen_costhetastar)".format(node)
## For v1->v1 checks:
#for node in range(2, 14):
#    sample_weights[ "cluster_node_rwgt_" + str(node) ] = "getBenchmarkReweighter().getWeight({}, hh_gen_mHH, hh_gen_costhetastar)".format(node)

# Plot configuration

# lljj 
weights_lljj = ['trigeff', 'llidiso', 'pu']
categories_lljj = ["All"] 
stage_lljj = "no_cut"
plots_lljj = ["mll", "mjj", "basic", "csv", "bdtinput", "gen"]

#llbb
weights_llbb = ['trigeff', 'llidiso', 'pu', 'jjbtag']
categories_llbb = ["All"]
stage_llbb = "no_cut"
plots_llbb = plots_lljj
#plots_llbb = ["bdtinput", "mjj"]

#systematics = {"modifObjects" : ["nominal"]}
systematics = {"modifObjects" : ["nominal", "jecup", "jecdown", "jerup", "jerdown"], "SF" : ["elidisoup", "elidisodown", "muidup", "muiddown", "muisoup", "muisodown", "jjbtagup", "jjbtagdown", "puup", "pudown", "trigeffup", "trigeffdown", "pdfup", "pdfdown", "scale", "scaleUncorr"]}
#systematics = {"modifObjects" : ["nominal"], "SF" : ["scale"]}

# Define binning of 2D templates for fitting
chosen2Dbinnings = {
        "3x25": {
            "mjjBinning": "3, { 0, 75, 140, 13000 }",
            "bdtNbins": 25
        },
        #"25x25": {
            #"mjjBinning": getBinningStrWithMax(25, 0, 600, 13000), 
            #"bdtNbins": 25
        #},
        #"20x20": {
            #"mjjBinning": getBinningStrWithMax(20, 0, 600, 13000), 
            #"bdtNbins": 20
        #},
        #"10x10": {
            #"mjjBinning": getBinningStrWithMax(10, 0, 600, 13000), 
            #"bdtNbins": 10
        #},
        #"10x25": {
            #"mjjBinning": getBinningStrWithMax(10, 0, 600, 13000), 
            #"bdtNbins": 25
        #},
        #"5x25": {
            #"mjjBinning": getBinningStrWithMax(5, 0, 600, 13000), 
            #"bdtNbins": 25
        #},
    }

for systematicType in systematics.keys():
    
    for systematic in systematics[systematicType]:
        if systematicType == "modifObjects":
            objects = systematic
        else:
            objects = "nominal" #ensure that we use normal hh_objects for systematics not modifying obect such as scale factors 

        ## lljj 
        basePlotter_lljj = BasePlotter(baseObjectName = "hh_llmetjj_HWWleptons_nobtag_csv", btagWP_str = 'nobtag', objects = objects)
        
        #plots.extend(basePlotter_lljj.generatePlots(categories_lljj, stage_lljj, systematic = systematic, weights = weights_lljj, requested_plots = plots_lljj))
        plots.extend(basePlotter_lljj.generatePlots(["All", "MuMu", "ElEl", "MuEl"], stage_lljj, systematic = systematic, weights = weights_lljj, requested_plots = ["mll"]))
        
        
        ## llbb 
        basePlotter_llbb = BasePlotter(baseObjectName = "hh_llmetjj_HWWleptons_btagM_csv", btagWP_str = 'medium', objects = objects)
       
        ## No mll cut
        #plots.extend(basePlotter_llbb.generatePlots(categories_llbb, stage_llbb, systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
        plots.extend(basePlotter_llbb.generatePlots(["All", "MuMu", "ElEl", "MuEl"], stage_llbb, systematic = systematic, weights = weights_llbb, requested_plots = ["mll"]))
        
        ## With mll cut
        plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "mll_cut", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
        plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "mll_cut", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput", "mjj", "mjj_vs_bdt"], fit2DtemplatesBinning = chosen2Dbinnings))

        # if systematic == 'nominal':
            # plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "mll_cut", systematic = systematic, weights = weights_llbb, requested_plots = ["llidisoWeight"], fit2DtemplatesBinning = chosen2Dbinnings))
        
        ## With mll cut + actually cut into mjj sidebands
        #plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "mjj_blind", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
        #plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "mjj_blind", systematic = systematic, weights = weights_llbb, requested_plots = ["bdtoutput"]))
        
        ## With mll cut + select into high-BDT regions
        #plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "highBDT_node_SM", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
        #plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "highBDT_node_2", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
