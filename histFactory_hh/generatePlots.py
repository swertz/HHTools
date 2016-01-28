import ROOT as R
import copy, sys, os, inspect 

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import *
from HHAnalysis import HH

plots = []
#basePlotter = BasePlotter()

mode = "custom"

plotFamilies = ["plots_lep", "plots_jet", "plots_met", "plots_ll", "plots_jj", "plots_llmetjj"] #,"plots_evt"]

if mode == "custom" :
    customString = "_allTight_btagL_csv" # not yet btag MM for last prod
    basePlotter = BasePlotter(mode = "custom", systematic = "nominal", baseObjectName = "hh_llmetjj"+customString)
    dict_cat_cut =  {
                    "ElEl" : "({0}.isElEl && elel_fire_trigger_Ele17_Ele12_cut && (runOnElEl || runOnMC) && {0}.p4.M() > 12)".format(basePlotter.ll_str),
                    "MuMu" : "({0}.isMuMu && (mumu_fire_trigger_Mu17_Mu8_cut || mumu_fire_trigger_Mu17_TkMu8_cut) && (runOnMuMu || runOnMC) && {0}.p4.M() > 12)".format(basePlotter.ll_str),
                    "MuEl" : "((({0}.isElMu && elmu_fire_trigger_Mu8_Ele17_cut) || ({0}.isMuEl && muel_fire_trigger_Mu17_Ele12_cut)) && (runOnElMu || runOnMC) && {0}.p4.M() > 12)".format(basePlotter.ll_str)
                    }
    cut_for_All_channel = dict_cat_cut["ElEl"] + "||" + dict_cat_cut["MuMu"] + "||" +dict_cat_cut["MuEl"]
    dict_cat_cut["All"] = cut_for_All_channel

    basePlotter.generatePlots(dict_cat_cut)
    for plotFamily in plotFamilies :
        for plot in getattr(basePlotter, plotFamily) :
            # scale factors
            plot["weight"] = "event_weight * event_pu_weight" 
            # can be uncommented as soon as this is adapted for the custom case
            #if not "scaleFactor" in plot["name"] : 
            #    plot["weight"] += " * " + get_leptons_SF(basePlotter.ll_str, basePlotter.lepid1, basePlotter.lepid2, basePlotter.lepiso1, basePlotter.lepiso2)
            #    plot["weight"] += " * " + get_csvv2_sf(basePlotter.btagWP1, basePlotter.jet1_fwkIdx)
            #    plot["weight"] += " * " + get_csvv2_sf(basePlotter.btagWP2, basePlotter.jet2_fwkIdx)
            plots.append(plot)

else : 
    # Order for llmetjj maps : lepid1, lepiso1, lepid2, lepiso2, jetid1, jetid2, btagWP1, btagWP2, pair
    workingPoints = [ ["T","T","T","T","L","L","no","no","csv"], ["T","T","T","T","L","L","L","L","csv"], ["T","T","T","T","L","L","M","M","csv"]]
    for WP in workingPoints :
        basePlotter = BasePlotter(mode = "map", systematic = "nominal", baseObjectName = "hh_llmetjj", WP = WP)
        basePlotter.extraCut = ""
        basePlotter.generatePlots(dict_cat_cut)

        for plotFamily in plotFamilies :
            for plot in getattr(basePlotter, plotFamily) :
                # scale factors
                plot["weight"] = "event_weight * event_pu_weight" 
                # can be uncommented as soon as this is adapted for the custom case
                #if not "scaleFactor" in plot["name"] : 
                #    plot["weight"] += " * " + get_leptons_SF(basePlotter.ll_str, basePlotter.lepid1, basePlotter.lepid2, basePlotter.lepiso1, basePlotter.lepiso2)
                #    plot["weight"] += " * " + get_csvv2_sf(basePlotter.btagWP1, basePlotter.jet1_fwkIdx)
                #    plot["weight"] += " * " + get_csvv2_sf(basePlotter.btagWP2, basePlotter.jet2_fwkIdx)
                plots.append(plot)

