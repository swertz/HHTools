import sys

sys.path.append("../histFactory_hh/")
from basePlotter import *
from HHAnalysis import HH
from ScaleFactors import *


# Generate once the list of variables for the tree, need one flavour choice 
# It is IRRELEVANT for the skimmer
customString = "_allTight_btagL_csv" # not yet btag MM for last prod
btagWP = "loose" # for the scale factors 
basePlotter = BasePlotter(mode = "custom", baseObjectName = "hh_llmetjj"+customString)
systematic = "nominal"
dict_stage_cut = {
        "bTagLooseNocut" : "", 
        "bTagLooseMllCut" : "(91.1876 - {0}.p4.M()) > 15".format(basePlotter.ll_str),
        "bTagLooseBdtCut" : "(91.1876 - {0}.p4.M()) > 15 && {0}.DR_l_l < 2.2 && {1}.DR_j_j < 3.1 && {2}.DPhi_ll_jj > 1.5".format(basePlotter.ll_str, basePlotter.jj_str, basePlotter.baseObject),
        "bTagLooseBdtCutMjjSB" : "(91.1876 - {0}.p4.M()) > 15 && {0}.DR_l_l < 2.2 && {1}.DR_j_j < 3.1 && {2}.DPhi_ll_jj > 1.5 && {1}.p4.M() < 60 && {1}.p4.M() > 160".format(basePlotter.ll_str, basePlotter.jj_str, basePlotter.baseObject)
                }

dict_cat_cut =  {
                "ElEl" : "({0}.isElEl && (elel_fire_trigger_Ele17_Ele12_cut || runOnMC) && (runOnElEl || runOnMC) && {0}.p4.M() > 12)".format(basePlotter.ll_str),
                "MuMu" : "({0}.isMuMu && (mumu_fire_trigger_Mu17_Mu8_cut || mumu_fire_trigger_Mu17_TkMu8_cuti || runOnMC) && (runOnMuMu || runOnMC) && {0}.p4.M() > 12)".format(basePlotter.ll_str),
                "MuEl" : "((({0}.isElMu && (elmu_fire_trigger_Mu8_Ele17_cut || runOnMC) || ({0}.isMuEl && (muel_fire_trigger_Mu17_Ele12_cut || runOnMC))) && (runOnElMu || runOnMC) && {0}.p4.M() > 12)".format(basePlotter.ll_str)
                }
cut_for_All_channel = "(" + dict_cat_cut["ElEl"] + "||" + dict_cat_cut["MuMu"] + "||" +dict_cat_cut["MuEl"] + ")"
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
llIdIso_sf = "(common::combineScaleFactors<2>({{{{({0}.isEl) ? electron_sf_hww_wp[{1}][0] : muon_sf_hww_wp[{1}][0], ({0}.isEl) ? electron_sf_hww_wp[{1}]{2} : muon_sf_hww_wp[{1}]{2}}}, {{ ({3}.isEl) ? electron_sf_hww_wp[{4}][0] : muon_sf_hww_wp[{4}][0], ({3}.isEl) ? electron_sf_hww_wp[{4}]{2} : muon_sf_hww_wp[{4}]{2} }}}}, {{{{1, 0}}, {{0, 1}}}}, common::Variation::{5}) )".format(basePlotter.lep1_str, basePlotter.lep1_fwkIdx, llIdIso_sfIdx, basePlotter.lep2_str, basePlotter.lep2_fwkIdx, llIdIso_strCommon)

# BTAG SF
jjBtag_sfIdx = "[0]"
jjBtag_strCommon="NOMINAL"
if systematic == "__jjBtagup":
    jjBtag_sfIdx = "[2]"
    jjBtag_strCommon="UP"
if systematic == "__jjBtagdown":
    jjBtag_sfIdx = "[1]"
    jjBtag_strCommon="DOWN"
jjBtag_sf = "(common::combineScaleFactors<2>({{{{ jet_sf_csvv2_{0}[{1}][0] , jet_sf_csvv2_{0}[{1}]{2} }}, {{ jet_sf_csvv2_{0}[{3}][0] , jet_sf_csvv2_{0}[{3}]{2} }}}}, {{{{1, 0}}, {{0, 1}}}}, common::Variation::{4}) )".format(btagWP, basePlotter.jet1_fwkIdx, jjBtag_sfIdx, basePlotter.jet2_fwkIdx, jjBtag_strCommon)

# PU WEIGHT
puWeight = "event_pu_weight"
if systematic == "__puup" :
    puWeight = "(event_pu_weight + event_pu_weight_up)"
if systematic == "__pudown" :
    puWeight = "(event_pu_weight - event_pu_weight_down)"

# TRIGGER EFFICIENCY
trigEff = "{0}.trigger_efficiency".format(basePlotter.ll_str)
if systematic == "__trigEffup" : 
    trigEff = "{0}.trigger_efficiency_upVariated".format(basePlotter.ll_str)
if systematic == "__trigEffdown" : 
    trigEff = "{0}.trigger_efficiency_downVariated".format(basePlotter.ll_str)

flavour = "All"
basePlotter.generatePlots({flavour: ""}, "", "noCut", weightsToPlot = {'trig_eff':trigEff, 'jj_btag_sf' : jjBtag_sf, 'll_idIso_sf' : llIdIso_sf, 'puWeight' : puWeight})

tree = {}
tree["name"] = "t"
tree["cut"] = dict_cat_cut["All"]
tree["branches"] = []

plotFamilies = ["plots_lep", "plots_jet", "plots_met", "plots_ll", "plots_jj", "plots_llmetjj", "plots_evt", "forSkimmer"]
for plotFamily in plotFamilies :
    for plot in getattr(basePlotter, plotFamily) :
        branch = {}
        branch["name"] = plot["name"].split("_"+flavour)[0]
        branch["variable"] = plot["variable"]
        tree["branches"].append(branch)

