import ROOT as R
import copy, sys, os, inspect 

# Usage from histFactory/plots/HHAnalysis/ : ./../../build/createHistoWithMultiDraw.exe -d ../../samples.json generatePlots.py 
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import *
from HHAnalysis import HH

plots = []

customString = "_allTight_btagL_csv" # not yet btag MM for last prod

basePlotter = BasePlotter(mode = "custom", systematic = "nominal", baseObjectName = "hh_llmetjj" + customString)

dict_cat_cut =  {
                "ElEl" : "({0}.isElEl && elel_fire_trigger_Ele17_Ele12_cut && (runOnElEl || runOnMC) && {0}.p4.M() > 12)".format(basePlotter.ll_str),
                "MuMu" : "({0}.isMuMu && (mumu_fire_trigger_Mu17_Mu8_cut || mumu_fire_trigger_Mu17_TkMu8_cut) && (runOnMuMu || runOnMC) && {0}.p4.M() > 12)".format(basePlotter.ll_str),
                "MuEl" : "((({0}.isElMu && elmu_fire_trigger_Mu8_Ele17_cut) || ({0}.isMuEl && muel_fire_trigger_Mu17_Ele12_cut)) && (runOnElMu || runOnMC) && {0}.p4.M() > 12)".format(basePlotter.ll_str)
                }
cut_for_All_channel = dict_cat_cut["ElEl"] + "||" + dict_cat_cut["MuMu"] + "||" +dict_cat_cut["MuEl"]
plots.append({
    "name" :  "jj_M_All" + customString + basePlotter.systematicString,
    "variable" : basePlotter.jj_str+".p4.M()",
    "plot_cut" : basePlotter.joinCuts(cut_for_All_channel, basePlotter.lepCut), #lepcut will be removed once we include it in HHAnalyzer,
    "binning" : "(100, 0, 400)"
})

# MVA evaluation : ugly but necessary part
includes = ["/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/HHTools/histFactory_hh/readMVA.h"]
baseStringForMVA_part1 = 'evaluateMVA("/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/HHTools/mvaTraining_hh/weights/BDTNAME_kBDT.weights.xml", '
baseStringForMVA_part2 = '{{"jj_pt", %s}, {"ll_pt", %s}, {"ll_M", %s}, {"ll_DR_l_l", %s}, {"jj_DR_j_j", %s}, {"llmetjj_DPhi_ll_jj", %s}, {"llmetjj_minDR_l_j", %s}, {"llmetjj_MTformula", %s}})'%(basePlotter.jj_str+".p4.Pt()", basePlotter.ll_str+".p4.Pt()", basePlotter.ll_str+".p4.M()", basePlotter.ll_str+".DR_l_l", basePlotter.jj_str+".DR_j_j", basePlotter.baseObject+".minDR_l_j", basePlotter.baseObject+".DPhi_ll_jj", basePlotter.baseObject+".MT_formula")

stringForMVA = baseStringForMVA_part1 + baseStringForMVA_part2

# The following will need to be modified each time the name of the BDT output changes
bdtNameTemplate = "DATE_BDT_XSPIN_MASS_SUFFIX"
date = "2016_01_17"
spins = ["0", "2"]
masses = ["400", "650", "900"]
suffixs = ["VS_TT09_DY01_8var_bTagMM"] #, "VS_TT1_DY0_8var_bTagMM"]

for spin in spins :
    for mass in masses :
        for suffix in suffixs :
            bdtName = bdtNameTemplate.replace("DATE", date).replace("SPIN", spin).replace("MASS", mass).replace("SUFFIX", suffix)
            stringForMVA = baseStringForMVA_part1.replace("BDTNAME", bdtName) + baseStringForMVA_part2
            plots.append({
                "name" : "MVA_%s_All%s%s"%(bdtName, customString, basePlotter.systematicString),
                "variable" : stringForMVA,
                "plot_cut" : basePlotter.joinCuts(cut_for_All_channel, basePlotter.lepCut), #lepcut will be removed once we include it in HHAnalyzer
                "binning" : "(50, -0.6, 0.6)",
                "weight" : "event_weight * event_pu_weight"
            })

# For next round : 
#                plot["weight"] += " * " + get_leptons_SF(basePlotter.ll_str, basePlotter.lepid1, basePlotter.lepid2, basePlotter.lepiso1, basePlotter.lepiso2)
#                plot["weight"] += " * " + get_csvv2_sf(basePlotter.btagWP1, basePlotter.jet1_fwkIdx)
#                plot["weight"] += " * " + get_csvv2_sf(basePlotter.btagWP2, basePlotter.jet2_fwkIdx)



