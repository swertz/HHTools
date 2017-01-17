import ROOT as R
import copy, sys, os, inspect 

scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import *
from HHAnalysis import HH

include_directories = []
plots = []
library_directories = []
libraries = []
sample_weights = {}

code_before_loop = default_code_before_loop()
code_in_loop = default_code_in_loop()
code_after_loop = default_code_after_loop()
headers = default_headers()

include_directories.append(os.path.join(scriptDir, "..", "common"))

###### Reweighting -- template-based #########
#sample_weights = {}

#headers.append("reweight_v1tov3.h")

## For v1->v3 reweighting
#code_before_loop += """
#getBenchmarkReweighter("/home/fynu/sbrochet/scratch/Framework/CMSSW_7_6_5/src/cp3_llbb/HHTools/scripts/", 0, 11, true, "cluster_NUM_v1_to_v3_weights.root", "NUM");
#"""
#for node in range(1, 13):
#    sample_weights[ "cluster_node_" + str(node) ] = "getBenchmarkReweighter().getWeight({}-1, hh_gen_mHH, hh_gen_costhetastar)".format(node)

## For v1->1507 reweighting
#code_before_loop += """
#getBenchmarkReweighter("/home/fynu/swertz/scratch/CMSSW_7_6_3_patch2/src/cp3_llbb/HHTools/scripts/weights_v1_1507_points.root", 0, 1506, false, "point_NUM_weights_unfolded", "NUM");
#"""
#for node in range(0, 1507):
#    if node in [324, 910, 985, 990]: continue # Skip dummy Xanda
#    sample_weights[ "point_" + str(node) ] = "getBenchmarkReweighter().getWeight({}, hh_gen_mHH, hh_gen_costhetastar)".format(node)

## For v1->v1 checks:
#code_before_loop += """
#getBenchmarkReweighter("/home/fynu/swertz/scratch/CMSSW_7_6_3_patch2/src/cp3_llbb/HHTools/scripts/", 2, 13, true, "cluster_NUM_v1_to_v3_weights.root", "NUM");
#"""
#for node in range(2, 14):
#    sample_weights[ "cluster_node_rwgt_" + str(node) ] = "getBenchmarkReweighter().getWeight({}, hh_gen_mHH, hh_gen_costhetastar)".format(node)

####### Reweighting -- ME-based #########
training_grid_reweighter = GridReweighting(scriptDir)

code_before_loop += training_grid_reweighter.before_loop()
code_in_loop += training_grid_reweighter.in_loop()
code_after_loop += training_grid_reweighter.after_loop()
include_directories += training_grid_reweighter.include_dirs()
headers += training_grid_reweighter.headers()
library_directories += training_grid_reweighter.library_dirs()
libraries += training_grid_reweighter.libraries()

sample_weights["training_grid"] = training_grid_reweighter.sample_weight()

### BM to MV term reweighting
##operators_MV = ["OtG", "Otphi", "O6", "OH"]
##rwgt_base = [ "SM", "box" ] + range(2, 13)
##for base, base_name in enumerate(rwgt_base):
##    for i, op1 in enumerate(operators_MV):
##        sample_weights["base_" + base_name + "_SM_" + op1] = "getHHEFTReweighter().getMVTermME(hh_gen_H1, hh_gen_H2, -1, {}, event_alpha_QCD)/getHHEFTReweighter().getBenchmarkME(hh_gen_H1, hh_gen_H2, {}, event_alpha_QCD)".format(i, base)
##        for j, op2 in enumerate(operators_MV):
##            if i < j: continue
##            sample_weights["base_" + base_name + "_" + op1 + "_" + op2] = "getHHEFTReweighter().getMVTermME(hh_gen_H1, hh_gen_H2, {}, {}, event_alpha_QCD)/getHHEFTReweighter().getBenchmarkME(hh_gen_H1, hh_gen_H2, {}, event_alpha_QCD)".format(i, j, base)

###########################"

# Plot configuration

#llbb
# weights_llbb = ['trigeff', 'llidiso', 'pu', 'jjbtag_heavy', 'jjbtag_light']

# FIXME: We don't have cMVAv2 SFs yet, so do not include b-tagging SFs
weights_llbb = ['trigeff', 'llidiso', 'pu']
categories_llbb = ["All", "MuMu", "ElEl", "MuEl"] 
plots_llbb = ["mll", "mjj", "basic", "cmva", "bdtinput", "evt", "dy_bdt_inputs", "dy_rwgt_bdt", "resonant_nnoutput", "nonresonant_nnoutput"]

# No systematics
systematics = {"modifObjects" : ["nominal"]}
# All systematics
#systematics = {"modifObjects" : ["nominal", "jecup", "jecdown", "jerup", "jerdown"], "SF" : ["elidisoup", "elidisodown", "muidup", "muiddown", "muisoup", "muisodown", "jjbtagup", "jjbtagdown", "puup", "pudown", "trigeffup", "trigeffdown", "pdfup", "pdfdown", "scale", "scaleUncorr"]}
# No b-tag SF systematics AND NO JEC/JER FOR NOW
#systematics = { "modifObjects": ["nominal"], "SF": ["elidisoup", "elidisodown", "muidup", "muiddown", "muisoup", "muisodown", "puup", "pudown", "trigeffup", "trigeffdown", "pdfup", "pdfdown", "scale", "scaleUncorr"] }

for systematicType in systematics.keys():
    
    for systematic in systematics[systematicType]:
        if systematicType == "modifObjects":
            objects = systematic
        else:
            objects = "nominal" #ensure that we use normal hh_objects for systematics not modifying obect such as scale factors 

        basePlotter_llbb = BasePlotter(baseObjectName = "hh_llmetjj_HWWleptons_btagM_cmva", btagWP_str = 'medium', objects = objects)
       
        plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "no_cut", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
        plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "mll_cut", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))
        plots.extend(basePlotter_llbb.generatePlots(categories_llbb, "inverted_mll_cut", systematic = systematic, weights = weights_llbb, requested_plots = plots_llbb))

        code_in_loop += basePlotter_llbb.get_code_in_loop()
        code_before_loop += basePlotter_llbb.get_code_before_loop()
        code_after_loop += basePlotter_llbb.get_code_after_loop()
