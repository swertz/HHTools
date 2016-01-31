import ROOT as R
import copy, sys, os, inspect 

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import *
from HHAnalysis import HH
includes = ["/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/HHTools/histFactory_hh/readMVA.h"]

plots = []
#basePlotter = BasePlotter()

mode = "custom"

plotFamilies = ["crucial_plots"] # ["plots_lep", "plots_jet", "plots_met", "plots_ll", "plots_jj", "plots_llmetjj", "plots_mva"] #,"plots_evt"]
systematics = {"modifObjects" : ["nominal", "jecup", "jecdown", "jerup", "jerdown"], "SF" : ["__llIdIsoup", "__llIdIsodown", "__jjBtagup", "__jjBtagdown", "__puup", "__pudown", "__trigEffup", "__trigEffdown"]}
#systematics = {"modifObjects" : ["nominal", "jecup"]}#, "jecdown", "jerup", "jerdown"], "SF" : ["__jjBtagup", "__jjBtagdown", "__trigEffup", "__trigEffdown"]}


for systematicType in systematics.keys() :
    for systematic in systematics[systematicType]:
        print systematic
        if systematicType == "modifObjects" :
            objects = systematic 
        else : 
            objects = "nominal" #ensure that we use normal hh_objects for systematics not modifying obect such as scale factors 

        if mode == "custom" :
            customStrings = {"nobtag" : "_allTight_nobtag_csv", "loose" : "_allTight_btagL_csv"} # name for lljj must be "nobtag"
            for btagStage in customStrings.keys() :
                basePlotter = BasePlotter(mode = "custom", baseObjectName = "hh_llmetjj"+customStrings[btagStage], systematic = objects)
                if systematicType != "modifObjects" :
                    basePlotter.systematicString = systematic

                dict_stage_cut = {
                        #"bTagLooseNocut" : "", 
                        #"bTagLooseMllCut" : "(91.1876 - {0}.p4.M()) > 15".format(basePlotter.ll_str),
                        "bTagLooseBdtCut" : "(91.1876 - {0}.p4.M()) > 15 && {0}.DR_l_l < 2.2 && {1}.DR_j_j < 3.1 && {2}.DPhi_ll_jj > 1.5".format(basePlotter.ll_str, basePlotter.jj_str, basePlotter.baseObject),
                        "bTagLooseBdtCutMjjSB" : "(91.1876 - {0}.p4.M()) > 15 && {0}.DR_l_l < 2.2 && {1}.DR_j_j < 3.1 && {2}.DPhi_ll_jj > 1.5 && {1}.p4.M() < 60 && {1}.p4.M() > 160".format(basePlotter.ll_str, basePlotter.jj_str, basePlotter.baseObject)
                                }
                
                dict_cat_cut =  {
                                "ElEl" : "({0}.isElEl && (hh_elel_fire_trigger_Ele17_Ele12_cut || runOnMC) && (runOnElEl || runOnMC) && {0}.p4.M() > 12)".format(basePlotter.ll_str),
                                "MuMu" : "({0}.isMuMu && (hh_mumu_fire_trigger_Mu17_Mu8_cut || hh_mumu_fire_trigger_Mu17_TkMu8_cut || runOnMC) && (runOnMuMu || runOnMC) && {0}.p4.M() > 12)".format(basePlotter.ll_str),
                                "MuEl" : "(({0}.isElMu && (hh_elmu_fire_trigger_Mu8_Ele17_cut || runOnMC) || ({0}.isMuEl && (hh_muel_fire_trigger_Mu17_Ele12_cut || runOnMC))) && (runOnElMu || runOnMC) && {0}.p4.M() > 12)".format(basePlotter.ll_str)
                                }
                cut_for_All_channel = "(" + dict_cat_cut["ElEl"] + "||" + dict_cat_cut["MuMu"] + "||" +dict_cat_cut["MuEl"] + ")"
                dict_cat_cut = {}
                dict_cat_cut["All"] = cut_for_All_channel

                # LEPTON SF
                llIdIso_sf = ""
                llIdIso_sfIdx = "[0]"
                llIdIso_strCommon="NOMINAL"
                if systematic == "__llIdIsoup" :
                    llIdIso_sfIdx = "[2]"
                    llIdIso_strCommon="UP"
                if systematic == "__llIdIsodown" :
                    llIdIso_sfIdx = "[1]"
                    llIdIso_strCommon="DOWN"
                llIdIso_sf = "(common::combineScaleFactors<2>({{{{{{({0}.isEl) ? electron_sf_hww_wp[{1}][0] : muon_sf_hww_wp[{1}][0], ({0}.isEl) ? electron_sf_hww_wp[{1}]{2} : muon_sf_hww_wp[{1}]{2}}}, {{ ({3}.isEl) ? electron_sf_hww_wp[{4}][0] : muon_sf_hww_wp[{4}][0], ({3}.isEl) ? electron_sf_hww_wp[{4}]{2} : muon_sf_hww_wp[{4}]{2} }}}}}}, {{{{1, 0}}, {{0, 1}}}}, common::Variation::{5}) )".format(basePlotter.lep1_str, basePlotter.lep1_fwkIdx, llIdIso_sfIdx, basePlotter.lep2_str, basePlotter.lep2_fwkIdx, llIdIso_strCommon)

                # BTAG SF
                jjBtag_sfIdx = "[0]"
                jjBtag_strCommon="NOMINAL"
                if systematic == "__jjBtagup":
                    jjBtag_sfIdx = "[2]"
                    jjBtag_strCommon="UP"
                if systematic == "__jjBtagdown":
                    jjBtag_sfIdx = "[1]"
                    jjBtag_strCommon="DOWN"
                jjBtag_sf = "(common::combineScaleFactors<2>({{{{{{ jet_sf_csvv2_{0}[{1}][0] , jet_sf_csvv2_{0}[{1}]{2} }}, {{ jet_sf_csvv2_{0}[{3}][0] , jet_sf_csvv2_{0}[{3}]{2} }}}}}}, {{{{1, 0}}, {{0, 1}}}}, common::Variation::{4}) )".format(btagStage, basePlotter.jet1_fwkIdx, jjBtag_sfIdx, basePlotter.jet2_fwkIdx, jjBtag_strCommon)

                # PU WEIGHT
                puWeight = "event_pu_weight"
                if systematic == "__puup" :
                    puWeight = "event_pu_weight_up"
                if systematic == "__pudown" :
                    puWeight = "event_pu_weight_down"

                # TRIGGER EFFICIENCY
                trigEff = "{0}.trigger_efficiency".format(basePlotter.ll_str)
                if systematic == "__trigEffup" : 
                    trigEff = "{0}.trigger_efficiency_upVariated".format(basePlotter.ll_str)
                if systematic == "__trigEffdown" : 
                    trigEff = "{0}.trigger_efficiency_downVariated".format(basePlotter.ll_str)
                
                # lljj plots
                if btagStage == "nobtag" :
                    basePlotter.generatePlots(dict_cat_cut, "", "noCut", weightsToPlot = {'trig_eff':trigEff, 'll_idIso_sf' : llIdIso_sf, 'puWeight' : puWeight})
                    for plotFamily in plotFamilies :
                        for plot in getattr(basePlotter, plotFamily) :
                            plot["weight"] = "event_weight" + " * " + puWeight + " * " + trigEff + " * " + llIdIso_sf 
                            plots.append(plot)
                        for plot in basePlotter.plots_weights :
                            plots.append(plot)
                # llbb plots
                else : 
                    for stage in dict_stage_cut.keys() :
                        basePlotter.generatePlots(dict_cat_cut, dict_stage_cut[stage], stage, weightsToPlot = {'trig_eff':trigEff, 'jj_btag_sf' : jjBtag_sf, 'll_idIso_sf' : llIdIso_sf, 'puWeight' : puWeight})
                        for plotFamily in plotFamilies :
                            for plot in getattr(basePlotter, plotFamily) :
                                # scale factors
                                plot["weight"] = "event_weight" + " * " + puWeight + " * " + trigEff + " * " + jjBtag_sf + " * " + llIdIso_sf 
                                plots.append(plot)
                        for plot in basePlotter.plots_weights :
                            plots.append(plot)

        else : 
            # Order for llmetjj maps : lepid1, lepiso1, lepid2, lepiso2, jetid1, jetid2, btagWP1, btagWP2, pair
            print "Deprecated Mode !!"
            workingPoints = [ ["T","T","T","T","L","L","no","no","csv"], ["T","T","T","T","L","L","L","L","csv"], ["T","T","T","T","L","L","M","M","csv"]]
            dict_cat_cut =  {
                            "ElEl" : "({0}.isElEl && elel_fire_trigger_Ele17_Ele12_cut && (runOnElEl || runOnMC) && {0}.p4.M() > 12)".format(basePlotter.ll_str),
                            "MuMu" : "({0}.isMuMu && (mumu_fire_trigger_Mu17_Mu8_cut || mumu_fire_trigger_Mu17_TkMu8_cut) && (runOnMuMu || runOnMC) && {0}.p4.M() > 12)".format(basePlotter.ll_str),
                            "MuEl" : "((({0}.isElMu && elmu_fire_trigger_Mu8_Ele17_cut) || ({0}.isMuEl && muel_fire_trigger_Mu17_Ele12_cut)) && (runOnElMu || runOnMC) && {0}.p4.M() > 12)".format(basePlotter.ll_str)
                            }
            for WP in workingPoints :
                basePlotter = BasePlotter(mode = "map", systematic = "nominal", baseObjectName = "hh_llmetjj", WP = WP)
                basePlotter.extraCut = ""
                basePlotter.generatePlots(dict_cat_cut)

                for plotFamily in plotFamilies :
                    for plot in getattr(basePlotter, plotFamily) :
                        # scale factors
                        plot["weight"] = "event_weight * event_pu_weight" 
                        if not "scaleFactor" in plot["name"] : 
                            plot["weight"] += " * " + get_leptons_SF(basePlotter.ll_str, basePlotter.lepid1, basePlotter.lepid2, basePlotter.lepiso1, basePlotter.lepiso2)
                            plot["weight"] += " * " + get_csvv2_sf(basePlotter.btagWP1, basePlotter.jet1_fwkIdx)
                            plot["weight"] += " * " + get_csvv2_sf(basePlotter.btagWP2, basePlotter.jet2_fwkIdx)
                        plots.append(plot)

