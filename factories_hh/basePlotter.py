import copy, sys, os

def default_code_before_loop():
    return r"""
        // Stuff for DY reweighting
        FWBTagEfficiencyOnBDT fwBtagEff("/nfs/scratch/fynu/sbrochet/Framework/CMSSW_8_0_24_patch1_HH_Analysis/src/cp3_llbb/HHTools/DYEstimation/170125_btaggingEfficiencyOnCondor_new_prod_DY/condor/output/btagging_efficiency.root", "/home/fynu/swertz/scratch/CMSSW_8_0_25/src/cp3_llbb/HHTools/DYEstimation/170123_bb_cc_vs_rest_10var_dyFlavorFractions_systematics/flavour_fractions.root", "/home/fynu/swertz/scratch/CMSSW_8_0_25/src/cp3_llbb/HHTools/DYEstimation/170123_bb_cc_vs_rest_10var_dyFlavorFractions_systematics/btagging_scale_factors.root");

        // DY BDT
        TMVAEvaluator dy_bdt_reader("/home/fynu/swertz/scratch/CMSSW_8_0_25/src/cp3_llbb/HHTools/DYEstimation/weights/2017_01_23_BDTDY_bb_cc_vs_rest_10var_kBDT.weights.xml", { "jet1_pt",  "jet1_eta", "jet2_pt", "jet2_eta", "jj_pt", "ll_pt", "ll_eta", "llmetjj_DPhi_ll_met", "ht", "nJetsL" });
        MVAEvaluatorCache<TMVAEvaluator> dy_bdt(dy_bdt_reader);
        
        bool isDY = m_dataset.name.find("DYJetsToLL") != std::string::npos;

        // Keras NN evaluation
        // Resonant
        KerasModelEvaluator resonant_nn("/home/fynu/sbrochet/scratch/Framework/CMSSW_8_0_24_patch1_HH_Analysis/src/cp3_llbb/HHTools/mvaTraining/hh_resonant_trained_models/2017-01-24_260_300_400_550_650_800_900_dy_estimation_from_BDT_new_prod_on_GPU_deeper_lr_scheduler_100epochs/hh_resonant_trained_model.h5");
        MVAEvaluatorCache<KerasModelEvaluator> resonant_nn_evaluator(resonant_nn);
        // Non-resonant
        KerasModelEvaluator nonresonant_nn("/home/fynu/sbrochet/scratch/Framework/CMSSW_8_0_24_patch1_HH_Analysis/src/cp3_llbb/HHTools/mvaTraining/hh_nonresonant_trained_models/2017-01-24_dy_estimation_from_BDT_new_prod_deeper_lr_scheduler_st_0p005_100epochs/hh_nonresonant_trained_model.h5");
        MVAEvaluatorCache<KerasModelEvaluator> nonresonant_nn_evaluator(nonresonant_nn);
"""

def default_code_in_loop():
    return r"""
        double HT = 0;
        for (size_t i = 0; i < hh_jets.size(); i++) {
            HT += hh_jets[i].p4.Pt();
        }
        for (size_t i = 0; i < hh_leptons.size(); i++) {
            HT += hh_leptons[i].p4.Pt();
        }

        resonant_nn_evaluator.clear();
        nonresonant_nn_evaluator.clear();
        dy_bdt.clear();
        
        fwBtagEff.clear_cache();
"""

def default_code_after_loop():
    return ""

def default_headers():
    return [
            "utils.h",
            "flavor_weighted_btag_efficiency_on_bdt.h",
            "KerasModelEvaluator.h",
            "TMVAEvaluator.h"
            ]

def default_include_directories(scriptDir):
    return [
            os.path.join(scriptDir, "..", "common", "include"),
            ]

def default_sources(scriptDir):
    files = [
            "utils.cc",
            "flavor_weighted_btag_efficiency_on_bdt.cc",
            "KerasModelEvaluator.cc",
            "TMVAEvaluator.cc"
            ]
    return [ os.path.join(scriptDir, "..", "common", "src", f) for f in files ]

def default_libraries():
    return []

class GridReweighting:
    def __init__(self, scriptDir):
        self.scriptDir = scriptDir

    def before_loop(self):
        return r'getHHEFTReweighter("{}");'.format( os.path.join(self.scriptDir, "..", "common", "MatrixElements") )

    def in_loop(self):
        return ""
    
    def after_loop(self):
        return ""

    def include_dirs(self):
        return [
                os.path.join(self.scriptDir, "..", "common", "MatrixElements", "pp_hh_5coup", "include"),
                os.path.join(self.scriptDir, "..", "common", "MatrixElements", "pp_hh_tree_MV", "include"),
                os.path.join(self.scriptDir, "..", "common", "include"),
                os.path.join(self.scriptDir, "..", "common"),
            ]

    def headers(self):
        return [
                "reweight_me.h",
            ]

    def library_dirs(self):
        return [
                os.path.join(self.scriptDir, "..", "common", "MatrixElements", "pp_hh_5coup", "build"),
                "/home/fynu/swertz/scratch/Madgraph/cmssw_madgraph_lp/pp_hh_all_MV_standalone/SubProcesses/P0_gg_hh/",
                "/home/fynu/swertz/scratch/Madgraph/cmssw_madgraph_lp/pp_hh_all_MV_standalone/SubProcesses/P1_gg_hh/",
                "/home/fynu/swertz/scratch/Madgraph/cmssw_madgraph_lp/pp_hh_all_MV_standalone/SubProcesses/P2_gg_hh/",
                os.path.join(self.scriptDir, "..", "common", "MatrixElements", "pp_hh_tree_MV", "build"),
            ]

    def libraries(self):
        return [
                "libme_pp_hh_5coup.a",
                "libhhWrapper0.a", "libhhWrapper1.a", "libhhWrapper2.a", "gfortran", "m", "quadmath",
                "libme_pp_hh_tree_MV_standalone.a",
            ]

    def sources(self):
        files = ["reweight_me.cc"]
        return [ os.path.join(self.scriptDir, "..", "common", "src", f) for f in files ]

    def sample_weight(self):
        return r"""
            getHHEFTReweighter().getACParamsME(hh_gen_H1, hh_gen_H2, { { "mdl_ctr", std::stod(sample_weight_args[1]) }, { "mdl_cy", std::stod(sample_weight_args[2]) }, {"mdl_c2",0},{"mdl_a1",0},{"mdl_a2",0} }, event_alpha_QCD)
            / getHHEFTReweighter().getBenchmarkME(hh_gen_H1, hh_gen_H2, std::stoi(sample_weight_args[0]), event_alpha_QCD)
            * getHHEFTReweighter().computeXS5(std::stoi(sample_weight_args[0])) 
            / getHHEFTReweighter().computeXS5({ { "mdl_ctr", std::stod(sample_weight_args[1]) }, { "mdl_cy", std::stod(sample_weight_args[2]) }, {"mdl_c2",0},{"mdl_a1",0},{"mdl_a2",0} })
            / std::stod(sample_weight_args[3])
            """

    

class BasePlotter:
    def __init__(self, baseObjectName, btagWP_str, objects="nominal"):
        # systematic should be jecup, jecdown, jerup or jerdown. The one for lepton, btag, etc, have to be treated with the "weight" parameter in generatePlots.py (so far)

        self.baseObject = baseObjectName+"[0]"
        self.suffix = baseObjectName
        self.btagWP_str = btagWP_str
        
        self.lep1_str = "hh_leptons[%s.ilep1]" % self.baseObject
        self.lep2_str = "hh_leptons[%s.ilep2]" % self.baseObject
        self.jet1_str = "hh_jets[%s.ijet1]" % self.baseObject
        self.jet2_str = "hh_jets[%s.ijet2]" % self.baseObject
        self.ll_str = "%s.ll_p4" % self.baseObject 
        self.jj_str = "%s.jj_p4" % self.baseObject

        if objects != "nominal":
            baseObjectName = baseObjectName.replace("hh_", "hh_" + objects + "_")
            self.lep1_str = self.lep1_str.replace("hh_", "hh_" + objects + "_")
            self.lep2_str = self.lep2_str.replace("hh_", "hh_" + objects + "_")
            self.jet1_str = self.jet1_str.replace("hh_", "hh_" + objects + "_")
            self.jet2_str = self.jet2_str.replace("hh_", "hh_" + objects + "_")
            self.ll_str = self.ll_str.replace("hh_", "hh_" + objects + "_")
            self.jj_str = self.jj_str.replace("hh_", "hh_" + objects + "_")
            self.baseObject = self.baseObject.replace("hh_", "hh_" + objects + "_")

        # needed to get scale factors (needs to be after the object modification due to systematics)
        self.lep1_fwkIdx = self.lep1_str + ".idx"
        self.lep2_fwkIdx = self.lep2_str + ".idx"
        self.jet1_fwkIdx = self.jet1_str + ".idx"
        self.jet2_fwkIdx = self.jet2_str + ".idx"

        # Ensure we have one candidate, works also for jecup etc
        self.sanityCheck = "Length$(%s)>0" % baseObjectName

        # Categories (lepton flavours)
        self.dict_cat_cut =  {
            "ElEl": "({0}.isElEl && (runOnElEl || runOnMC) && {1}.M() > 12)".format(self.baseObject, self.ll_str),
            "MuMu": "({0}.isMuMu && (runOnMuMu || runOnMC) && {1}.M() > 12)".format(self.baseObject, self.ll_str),
            "MuEl": "(({0}.isElMu || {0}.isMuEl) && (runOnElMu || runOnMC) && {1}.M() > 12)".format(self.baseObject, self.ll_str)
                        }
        cut_for_All_channel = "(" + self.dict_cat_cut["ElEl"] + "||" + self.dict_cat_cut["MuMu"] + "||" +self.dict_cat_cut["MuEl"] + ")"
        cut_for_SF_channel = "(" + self.dict_cat_cut["ElEl"] + "||" + self.dict_cat_cut["MuMu"] + ")"
        self.dict_cat_cut["SF"] = cut_for_SF_channel
        self.dict_cat_cut["All"] = cut_for_All_channel

    
    
    def generatePlots(self, categories, stage, requested_plots, weights, systematic="nominal", extraString="", prependCuts=[], appendCuts=[], allowWeightedData=False):

        # Protect against the fact that data do not have jecup collections, in the nominal case we still have to check that data have one candidate 
        sanityCheck = self.sanityCheck
        if systematic != "nominal" and not allowWeightedData:
            sanityCheck = self.joinCuts("!event_is_data", self.sanityCheck)

        cuts = self.joinCuts(*(prependCuts + [sanityCheck]))

        # Possible stages (selection)
        # FIXME: Move to constructor
        mll_cut = "((91 - {0}.M()) > 15)".format(self.ll_str)
        inverted_mll_cut = "((91 - {0}.M()) <= 15)".format(self.ll_str)
        high_mll_cut = "(({0}.M() - 91) > 15)".format(self.ll_str)
        mjj_blind = "({0}.M() < 75 || {0}.M() > 140)".format(self.jj_str)

        dict_stage_cut = {
               "no_cut": "", 
               "mll_cut": mll_cut,
               "inverted_mll_cut": inverted_mll_cut,
               "high_mll_cut": high_mll_cut,
               "mjj_blind": self.joinCuts(mjj_blind, mll_cut),
               }

        # Keras neural network
        keras_resonant_input_variables = '{%s, %s, %s, %s, %s, %s, %s, %s, (double) %s, %%d}' % (self.jj_str + ".Pt()", self.ll_str + ".Pt()", self.ll_str + ".M()", self.baseObject + ".DR_l_l", self.baseObject + ".DR_j_j", self.baseObject + ".DPhi_ll_jj", self.baseObject + ".minDR_l_j", self.baseObject + ".MT_formula", self.baseObject + ".isSF")
        keras_nonresonant_input_variables = '{%s, %s, %s, %s, %s, %s, %s, %s, (double) %s, %%f, %%f}' % (self.jj_str + ".Pt()", self.ll_str + ".Pt()", self.ll_str + ".M()", self.baseObject + ".DR_l_l", self.baseObject + ".DR_j_j", self.baseObject + ".DPhi_ll_jj", self.baseObject + ".minDR_l_j", self.baseObject + ".MT_formula", self.baseObject + ".isSF")
        
        # Keras resonant NN
        resonant_signal_masses = [260, 300, 400, 550, 650, 800, 900]
        restricted_resonant_signals = [260, 400, 900] # For 1D plots, only select a few points

        # Keras non-resonant NN
        nonresonant_signal_grid = [ (kl, kt) for kl in [-20, 0.0001, 1, 2.4, 3.8, 5, 20] for kt in [0.5, 1, 1.75, 2.5] ]
        nonresonant_grid_shift = { "kl": 20.0, "kt": 0 } # Shift parameters to be positive everywhere (goes in line with the training)
        restricted_nonresonant_signals = [ (1, 1), (2.4, 2.5), (-20, 0.5) ] # For 1D plots, only select a few points

        ###########
        # Weights #
        ###########

        # Lepton ID and Iso Scale Factors
        llIdIso_sfIdx = "[0]"
        llIdIso_strCommon = "NOMINAL"
        llIdIso_sf = "(common::combineScaleFactors<2>({{{{{{({0}.isEl) ? electron_sf_hww_wp[{1}][0] : muon_sf_id_tight_hww[{1}][0]*muon_sf_iso_tight_hww[{1}][0], ({0}.isEl) ? electron_sf_hww_wp[{1}]{2} : muon_sf_id_tight_hww[{1}]{2}*muon_sf_iso_tight_hww[{1}]{2}}}, {{ ({3}.isEl) ? electron_sf_hww_wp[{4}][0] : muon_sf_id_tight_hww[{4}][0]*muon_sf_iso_tight_hww[{4}][0], ({3}.isEl) ? electron_sf_hww_wp[{4}]{2} : muon_sf_id_tight_hww[{4}]{2}*muon_sf_iso_tight_hww[{4}]{2} }}}}}}, common::Variation::{5}) )".format(self.lep1_str, self.lep1_fwkIdx, llIdIso_sfIdx, self.lep2_str, self.lep2_fwkIdx, llIdIso_strCommon)
        # electrons
        if systematic == "elidisoup":
            llIdIso_sfIdx = "[2]" 
            llIdIso_strCommon = "UP"
        if systematic == "elidisodown":
            llIdIso_sfIdx = "[1]"
            llIdIso_strCommon = "DOWN"
        if systematic == "elidisoup" or systematic == "elidisodown":
            llIdIso_sf = "(common::combineScaleFactors<2>({{{{{{({0}.isEl) ? electron_sf_hww_wp[{1}][0] :muon_sf_id_tight_hww[{1}][0]*muon_sf_iso_tight_hww[{1}][0], ({0}.isEl) ? electron_sf_hww_wp[{1}]{2} : 0 }}, {{ ({3}.isEl) ? electron_sf_hww_wp[{4}][0] :muon_sf_id_tight_hww[{4}][0]*muon_sf_iso_tight_hww[{4}][0], ({3}.isEl) ? electron_sf_hww_wp[{4}]{2} : 0 }}}}}}, common::Variation::{5}) )".format(self.lep1_str, self.lep1_fwkIdx, llIdIso_sfIdx, self.lep2_str, self.lep2_fwkIdx, llIdIso_strCommon)

        # muons
        if systematic == "muidup":
            llIdIso_sfIdx = "[2]" 
            llIdIso_strCommon="UP"
        if systematic == "muiddown":
            llIdIso_sfIdx = "[1]"
            llIdIso_strCommon="DOWN"
        if systematic == "muidup" or systematic == "muiddown":
            # if we compute muon id error, the muon iso SF should not be inside the combineScaleFactors (above, for electron id error, it can be inside because it won't be use together with the error
            llIdIso_sf = "((({0}.isEl) ? 1 : muon_sf_iso_tight_hww[{1}][0]) * (({3}.isEl) ? 1 : muon_sf_iso_tight_hww[{4}][0]) * (common::combineScaleFactors<2>({{{{{{({0}.isEl) ? electron_sf_hww_wp[{1}][0] :muon_sf_id_tight_hww[{1}][0], ({0}.isEl) ? 0. :muon_sf_id_tight_hww[{1}]{2}}}, {{ ({3}.isEl) ? electron_sf_hww_wp[{4}][0] :muon_sf_id_tight_hww[{4}][0], ({3}.isEl) ? 0. :muon_sf_id_tight_hww[{4}]{2} }}}}}}, common::Variation::{5}) ))".format(self.lep1_str, self.lep1_fwkIdx, llIdIso_sfIdx, self.lep2_str, self.lep2_fwkIdx, llIdIso_strCommon)
        if systematic == "muisoup":
            llIdIso_sfIdx = "[2]" 
            llIdIso_strCommon="UP"
        if systematic == "muisodown":
            llIdIso_sfIdx = "[1]"
            llIdIso_strCommon="DOWN"
        if systematic == "muisoup" or systematic == "muisodown":
            llIdIso_sf = "((({0}.isEl) ? 1 : muon_sf_id_tight_hww[{1}][0]) * (({3}.isEl) ? 1 : muon_sf_id_tight_hww[{4}][0]) * (common::combineScaleFactors<2>({{{{{{({0}.isEl) ? electron_sf_hww_wp[{1}][0] :muon_sf_iso_tight_hww[{1}][0], ({0}.isEl) ? 0. :muon_sf_iso_tight_hww[{1}]{2}}}, {{ ({3}.isEl) ? electron_sf_hww_wp[{4}][0] :muon_sf_iso_tight_hww[{4}][0], ({3}.isEl) ? 0. :muon_sf_iso_tight_hww[{4}]{2} }}}}}}, common::Variation::{5}) ))".format(self.lep1_str, self.lep1_fwkIdx, llIdIso_sfIdx, self.lep2_str, self.lep2_fwkIdx, llIdIso_strCommon)

        # propagate jecup etc to the framework objects
        sys_fwk = ""

        if "jec" in systematic or "jer" in systematic:
            sys_fwk = "_" + systematic

        # BTAG SF, only applied if requesting b-tags
        if self.btagWP_str != 'nobtag':
            jjBtag_light_sfIdx = "[0]"
            jjBtag_light_strCommon="NOMINAL"
            if systematic == "jjbtaglightup":
                jjBtag_light_sfIdx = "[2]" 
                jjBtag_light_strCommon="UP"
            if systematic == "jjbtaglightdown":
                jjBtag_light_sfIdx = "[1]"
                jjBtag_light_strCommon="DOWN"
            
            jjBtag_heavy_sfIdx = "[0]"
            jjBtag_heavy_strCommon="NOMINAL"
            if systematic == "jjbtagheavyup":
                jjBtag_heavy_sfIdx = "[2]" 
                jjBtag_heavy_strCommon="UP"
            if systematic == "jjbtagheavydown":
                jjBtag_heavy_sfIdx = "[1]"
                jjBtag_heavy_strCommon="DOWN"

            jjBtag_heavyjet_sf = "(common::combineScaleFactors<2>({{ {{ {{ jet{0}_sf_cmvav2_heavyjet_{1}[{2}][0] , jet{0}_sf_cmvav2_heavyjet_{1}[{2}]{3} }}, {{ jet{0}_sf_cmvav2_heavyjet_{1}[{4}][0], jet{0}_sf_cmvav2_heavyjet_{1}[{4}]{3} }} }} }}, common::Variation::{5}) )".format(sys_fwk, self.btagWP_str, self.jet1_fwkIdx, jjBtag_heavy_sfIdx, self.jet2_fwkIdx, jjBtag_heavy_strCommon)

            ## FIXME WARNING MINIMUM SET AT 0.8 / +-0.07
            jjBtag_lightjet_sf = "(common::combineScaleFactors<2>({{ {{ {{ std::max((float)0.8, (float)jet{0}_sf_cmvav2_lightjet_{1}[{2}][0]), std::max((float)0.07, (float)jet{0}_sf_cmvav2_lightjet_{1}[{2}]{3}) }}, {{ std::max((float)0.8, (float)jet{0}_sf_cmvav2_lightjet_{1}[{4}][0]), std::max((float)0.07, (float)jet{0}_sf_cmvav2_lightjet_{1}[{4}]{3}) }} }} }}, common::Variation::{5}) )".format(sys_fwk, self.btagWP_str, self.jet1_fwkIdx, jjBtag_light_sfIdx, self.jet2_fwkIdx, jjBtag_light_strCommon)
            #jjBtag_lightjet_sf = "(common::combineScaleFactors<2>({{ {{ {{ jet{0}_sf_cmvav2_lightjet_{1}[{2}][0] , jet{0}_sf_cmvav2_lightjet_{1}[{2}]{3} }},{{ jet{0}_sf_cmvav2_lightjet_{1}[{4}][0], jet{0}_sf_cmvav2_lightjet_{1}[{4}]{3} }} }} }}, common::Variation::{5}) )".format(sys_fwk, self.btagWP_str, self.jet1_fwkIdx, jjBtag_light_sfIdx, self.jet2_fwkIdx, jjBtag_light_strCommon)

        else:
            jjBtag_heavyjet_sf = "1."
            jjBtag_lightjet_sf = "1."

        # PU WEIGHT
        puWeight = "event_pu_weight"
        if systematic == "puup":
            puWeight = "event_pu_weight_up"
        if systematic == "pudown":
            puWeight = "event_pu_weight_down"

        # PDF weight
        pdfWeight = ""
        normalization = "nominal"
        if systematic == "pdfup": # do not change the name of "pdfup", use latter for the proper normalization
            pdfWeight = "event_pdf_weight_up"
            normalization = "pdf_up"
        if systematic == "pdfdown":
            pdfWeight = "event_pdf_weight_down"
            normalization = "pdf_down"

        # TRIGGER EFFICIENCY
        trigEff = "({0}.trigger_efficiency)".format(self.baseObject)
        if systematic == "trigeffup":
            trigEff = "({0}.trigger_efficiency_upVariated)".format(self.baseObject)
        if systematic == "trigeffdown":
            trigEff = "({0}.trigger_efficiency_downVariated)".format(self.baseObject)
        # Include dZ filter efficiency for ee (not for mumu since we no longer use the DZ version of the trigger)
        # FIXME
        trigEff += "*(({0}.isElEl && runOnMC) ? 0.995 : 1)".format(self.baseObject)

        # Append the proper extension to the name plot if needed
        self.systematicString = ""
        if not systematic == "nominal":
            self.systematicString = "__" + systematic

        # DY BDT reweighting
        dy_bdt_variables = [
                self.jet1_str + ".p4.Pt()",
                self.jet1_str + ".p4.Eta()",
                self.jet2_str + ".p4.Pt()",
                self.jet2_str + ".p4.Eta()",
                self.jj_str + ".Pt()",
                self.ll_str + ".Pt()",
                self.ll_str + ".Eta()",
                "abs(" + self.baseObject + ".DPhi_ll_met)",
                "HT",
                "(double) hh_nJetsL",
            ]
        dy_bdt_variables_string = "{ " + ", ".join(dy_bdt_variables) + " }"
        
        dy_nobtag_to_btagM_weight_BDT = 'fwBtagEff.get_cached({0}, {1}, dy_bdt.evaluate({2}), "{3}")'.format(self.jet1_str + ".p4", self.jet2_str + ".p4", dy_bdt_variables_string, systematic)

        available_weights = {
                'trigeff': trigEff,
                'jjbtag_heavy': jjBtag_heavyjet_sf,
                'jjbtag_light': jjBtag_lightjet_sf,
                'llidiso': llIdIso_sf,
                'pu': puWeight,
                'dy_nobtag_to_btagM_BDT': dy_nobtag_to_btagM_weight_BDT,
                }
        
        #########
        # PLOTS #
        #########
        self.basic_plot = []
        self.csv_plot = []
        self.cmva_plot = []
        self.nn_inputs_plot = []
        self.isElEl_plot = []
        self.mjj_plot = []
 
        self.mjj_vs_resonant_nnoutput_plot = []
        self.mjj_vs_nonresonant_nnoutput_plot = []
        self.resonant_nnoutput_plot = []
        self.nonresonant_nnoutput_plot = []

        self.flavour_plot = []
        self.detailed_flavour_plot = []

        self.llidisoWeight_plot = []
        self.mumuidisoWeight_plot = []
        self.elelidisoWeight_plot = []
        self.jjbtagWeight_plot = []
        self.trigeffWeight_plot = []
        self.puWeight_plot = []
        self.scaleWeight_plot = []
        self.pdfWeight_plot = []
        self.DYNobtagToBTagMWeight_plot = []
        
        self.gen_plot = []
        self.evt_plot = []

        self.dy_rwgt_bdt_plot = []
        self.dy_rwgt_bdt_flavour_plot = []
        self.dy_bdt_inputs_plot = []

        self.other_plot = []
        self.vertex_plot = []
        self.genht_plot = []

        self.forSkimmer_plot = []

        for cat in categories:

            catCut = self.dict_cat_cut[cat]
            self.totalCut = self.joinCuts(cuts, catCut, dict_stage_cut[stage], *appendCuts)
            
            self.llFlav = cat
            self.extraString = stage + extraString

            self.mjj_plot.append({
                        'name': 'jj_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jj_str + ".M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 10, 410)'
                })
            
            # Plot to compute yields (ensure we have not over/under flow)
            self.isElEl_plot.append({
                        'name': 'isElEl_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "%s.isElEl"%self.baseObject,
                        'plot_cut': self.totalCut,
                        'binning': '(2, 0, 2)'
                })
            
            # Neural network output
            for m in resonant_signal_masses:
                if m in restricted_resonant_signals:
                    self.resonant_nnoutput_plot.append({
                            'name': 'NN_resonant_M%d_%s_%s_%s%s' % (m, self.llFlav, self.suffix, self.extraString, self.systematicString),
                            'variable': 'resonant_nn_evaluator.evaluate(%s)' % (keras_resonant_input_variables % m),
                            'plot_cut': self.totalCut,
                            'binning': '(50, {}, {})'.format(0, 1)
                    })
                self.mjj_vs_resonant_nnoutput_plot.append({
                        'name': 'mjj_vs_NN_resonant_M%d_%s_%s_%s%s' % (m, self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jj_str + '.M() ::: resonant_nn_evaluator.evaluate(%s)' % (keras_resonant_input_variables % m),
                        'plot_cut': self.totalCut,
                        'binning': '(3, { 0, 75, 140, 13000 }, 25, 0, 1)'
                })
            for point in nonresonant_signal_grid:
                kl = point[0]
                kt = point[1]
                point_str = "point_{}_{}".format(kl, kt).replace(".", "p").replace("-", "m")
                kl += nonresonant_grid_shift["kl"]
                kt += nonresonant_grid_shift["kt"]
                if point in restricted_nonresonant_signals:
                    self.nonresonant_nnoutput_plot.append({
                            'name': 'NN_nonresonant_%s_%s_%s_%s%s' % (point_str, self.llFlav, self.suffix, self.extraString, self.systematicString),
                            'variable': 'nonresonant_nn_evaluator.evaluate(%s)' % (keras_nonresonant_input_variables % (kl, kt)),
                            'plot_cut': self.totalCut,
                            'binning': '(50, {}, {})'.format(0, 1)
                    })
                self.mjj_vs_nonresonant_nnoutput_plot.append({
                        'name': 'mjj_vs_NN_nonresonant_%s_%s_%s_%s%s' % (point_str, self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jj_str + '.M() ::: nonresonant_nn_evaluator.evaluate(%s)' % (keras_nonresonant_input_variables % (kl, kt)),
                        'plot_cut': self.totalCut,
                        'binning': '(3, { 0, 75, 140, 13000 }, 25, 0, 1)'
                })
            
            # DY reweighting plots
            dy_bdt_flat_binning = '(40, {-0.5139261638387755, -0.28898196567405476, -0.2476582749856528, -0.21996646493207206, -0.1991670200454712, -0.18167569032901326, -0.16599964930321504, -0.15156757188594833, -0.13818661103236354, -0.12567874006226315, -0.11381442895759973, -0.10263199524142008, -0.09196628930949025, -0.08190636298862279, -0.0722791277618637, -0.06310992276046588, -0.05426600234483494, -0.04569692655758403, -0.03740621352909089, -0.029288264245728928, -0.021465863317879297, -0.013527078590598906, -0.005835657418566017, 0.001713033791860969, 0.009345489580270679, 0.016925843221660714, 0.02461982942842052, 0.03227487210746482, 0.04026572735765449, 0.04846055203674637, 0.057014862886138835, 0.06595620832498035, 0.07527427505752232, 0.08502963174016062, 0.09567345692228932, 0.10739628516126071, 0.12074974301699766, 0.1368035706668398, 0.15707625645811507, 0.18698084196962542, 0.237, 0.287, 0.337, 0.38725443171761686})'
            self.dy_rwgt_bdt_plot.extend([
                {
                    'name': 'DY_BDT_flat_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': 'dy_bdt.evaluate({})'.format(dy_bdt_variables_string),
                    'plot_cut': self.totalCut,
                    # 161220, bb_cc_vs_rest_10var:
                    'binning': dy_bdt_flat_binning,
                },
                {
                    'name': 'DY_BDT_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': 'dy_bdt.evaluate({})'.format(dy_bdt_variables_string),
                    'plot_cut': self.totalCut,
                    'binning': '(50, -0.5, 0.4)',
                },
            ])
            for flav1 in ["b", "c", "l"]:
                for flav2 in ["b", "c", "l"]:
                    flavour_cut = "({0}.gen_{2} && {1}.gen_{3})".format(self.jet1_str, self.jet2_str, flav1, flav2)
                    self.dy_rwgt_bdt_flavour_plot.append({
                            'name': 'DY_BDT_flav_%s%s_%s_%s_%s%s' % (flav1, flav2, self.llFlav, self.suffix, self.extraString, self.systematicString),
                            'variable': 'dy_bdt.evaluate({})'.format(dy_bdt_variables_string),
                            'plot_cut': self.joinCuts(self.totalCut, flavour_cut),
                            'binning': dy_bdt_flat_binning,
                        })


            # Weight Plots
            self.jjbtagWeight_plot.append(
                        {'name': 'jjbtag_heavy_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString,  self.systematicString), 'variable': available_weights["jjbtag_heavy"],
                        'plot_cut': self.totalCut, 'binning':'(100, 0, 1.5)', 'weight': 'event_weight'})
            self.jjbtagWeight_plot.append(
                        {'name': 'jjbtag_light_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString,  self.systematicString), 'variable': available_weights["jjbtag_light"],
                        'plot_cut': self.totalCut, 'binning':'(100, 0, 1.5)', 'weight': 'event_weight'})
            self.llidisoWeight_plot.append(
                        {'name': 'llidiso_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString,  self.systematicString), 'variable': available_weights["llidiso"],
                        'plot_cut': self.totalCut, 'binning': '(50, 0.7, 1.3)', 'weight': 'event_weight'})
            self.llidisoWeight_plot.append(
                        {'name': 'mumuidiso_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString,  self.systematicString), 'variable': available_weights["llidiso"],
                        'plot_cut': self.joinCuts(self.totalCut, "%s.isMuMu" % self.baseObject), 'binning': '(50, 0.7, 1.3)', 'weight': 'event_weight'})
            self.llidisoWeight_plot.append(
                        {'name': 'elelidiso_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString,  self.systematicString), 'variable': available_weights["llidiso"],
                        'plot_cut': self.joinCuts(self.totalCut, "%s.isElEl" % self.baseObject), 'binning': '(50, 0.7, 1.3)', 'weight': 'event_weight'})
            self.trigeffWeight_plot.append(
                        {'name': 'trigeff_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString,  self.systematicString), 'variable': available_weights["trigeff"],
                        'plot_cut': self.totalCut, 'binning': '(50, 0, 1.2)', 'weight': 'event_weight'})
            self.puWeight_plot.append(
                        {'name': 'pu_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString,  self.systematicString), 'variable': available_weights["pu"],
                        'plot_cut': self.totalCut, 'binning': '(100, 0, 4)', 'weight': 'event_weight'})
            self.DYNobtagToBTagMWeight_plot.append(
                        {'name': 'dy_nobtag_to_btagM_weight_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString,  self.systematicString), 'variable': available_weights["dy_nobtag_to_btagM_BDT"],
                        'plot_cut': self.totalCut, 'binning': '(50, 0, 0.05)', 'weight': 'event_weight'})

            self.scaleWeight_plot.extend([
                        {'name': 'scale0_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString,  self.systematicString), 'variable': "std::abs(event_scale_weights[0])",
                        'plot_cut': self.totalCut, 'binning': '(100, 0, 2)', 'weight': 'event_weight'},
                        {'name': 'scale1_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString,  self.systematicString), 'variable': "std::abs(event_scale_weights[1])",
                        'plot_cut': self.totalCut, 'binning': '(100, 0, 2)', 'weight': 'event_weight'},
                        {'name': 'scale2_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString,  self.systematicString), 'variable': "std::abs(event_scale_weights[2])",
                        'plot_cut': self.totalCut, 'binning': '(100, 0, 2)', 'weight': 'event_weight'},
                        {'name': 'scale3_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString,  self.systematicString), 'variable': "std::abs(event_scale_weights[3])",
                        'plot_cut': self.totalCut, 'binning': '(100, 0, 2)', 'weight': 'event_weight'},
                        {'name': 'scale4_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString,  self.systematicString), 'variable': "std::abs(event_scale_weights[4])",
                        'plot_cut': self.totalCut, 'binning': '(100, 0, 2)', 'weight': 'event_weight'},
                        {'name': 'scale5_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString,  self.systematicString), 'variable': "std::abs(event_scale_weights[5])",
                        'plot_cut': self.totalCut, 'binning': '(100, 0, 2)', 'weight': 'event_weight'}])
                    
            # BASIC PLOTS
            self.basic_plot.extend([
                {
                        'name': 'lep1_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.lep1_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 20, 400)'
                },
                {
                        'name': 'lep2_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.lep2_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 10, 200)'
                },
                {
                        'name': 'jet1_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 20, 500)'
                },
                {
                        'name': 'jet2_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 20, 300)'
                },
                {
                        'name': 'met_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "met_p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 500)'
                },
                {
                        'name': 'ht_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "HT",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 65, 1500)'
                },
                {
                        'name': 'llmetjj_MT2_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".MT2",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 500)'
                },
                {
                        'name': 'llmetjj_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".p4.M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 100, 1500)'
                },
                {
                        'name': 'cosThetaStar_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject + ".cosThetaStar_CS",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 1)'
                },
            ])
            
            self.csv_plot.extend([
                {
                        'name': 'jet1_CSV_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".CSV",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 1)'
                },
                {
                        'name': 'jet2_CSV_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".CSV",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 1)'
                }
            ])
            
            self.cmva_plot.extend([
                {
                        'name': 'jet1_cMVAv2_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".CMVAv2",
                        'plot_cut': self.totalCut,
                        'binning': '(50, -1, 1)'
                },
                {
                        'name': 'jet2_cMVAv2_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".CMVAv2",
                        'plot_cut': self.totalCut,
                        'binning': '(50, -1, 1)'
                }
            ])
            
            self.nn_inputs_plot.extend([
                {
                        'name': 'll_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.ll_str+".M()",
                        'plot_cut': self.totalCut,
                        'binning': '(60, 12, 252)'
                },
                {
                        'name': 'll_DR_l_l_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".DR_l_l",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name': 'jj_DR_j_j_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".DR_j_j",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name': 'llmetjj_DPhi_ll_jj_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".DPhi_ll_jj)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                },
                {
                        'name': 'll_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.ll_str+".Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 450)'
                },
                {
                        'name': 'jj_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jj_str+".Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 450)'
                },
                {
                        'name': 'llmetjj_minDR_l_j_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".minDR_l_j",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 5)'
                },
                {
                        'name': 'llmetjj_MTformula_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".MT_formula", # std::sqrt(2 * ll[ill].p4.Pt() * met[imet].p4.Pt() * (1-std::cos(dphi)));
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 500)'
                },
            ])

            self.dy_bdt_inputs_plot.extend([
                {
                        'name': 'jet1_eta_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".p4.Eta()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -2.5, 2.5)'
                },
                {
                        'name': 'jet2_eta_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".p4.Eta()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -2.5, 2.5)'
                },
                {
                        'name': 'll_eta_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject + ".ll_p4.Eta()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, -5, 5)'
                },
                {
                        'name': 'llmetjj_DPhi_ll_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".DPhi_ll_met)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                },
            ])

            self.other_plot.extend([
                {
                    'name': 'lep1_eta_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': self.lep1_str+".p4.Eta()",
                    'plot_cut': self.totalCut,
                    'binning': '(25, -2.5, 2.5)'
                },
                {
                    'name': 'lep1_phi_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': self.lep1_str+".p4.Phi()",
                    'plot_cut': self.totalCut,
                    'binning': '(25, -3.1416, 3.1416)'
                },
                #{
                #    'name': 'lep1_scaleFactor_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #    'variable': get_lepton_SF(self.lep1_str, self.lepid1, self.lepiso1, "nominal"),
                #    'plot_cut': self.totalCut,
                #    'binning': '(50, 0.8, 1.2)'
                #},
                {
                    'name': 'lep1_Iso_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "({0}.isEl) ? electron_relativeIsoR03_withEA[{1}] : muon_relativeIsoR04_deltaBeta[{1}]".format(self.lep1_str, self.lep1_fwkIdx),
                    'plot_cut': self.totalCut,
                    'binning': '(50, 0, 0.4)'
                },
                {
                    'name': 'lep2_eta_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': self.lep2_str+".p4.Eta()",
                    'plot_cut': self.totalCut,
                    'binning': '(25, -2.5, 2.5)'
                },
                {
                    'name': 'lep2_phi_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': self.lep2_str+".p4.Phi()",
                    'plot_cut': self.totalCut,
                    'binning': '(25, -3.1416, 3.1416)'
                },
                #{
                #    'name': 'lep2_scaleFactor_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #    'variable': get_lepton_SF(self.lep2_str, self.lepid2, self.lepiso2, "nominal"),
                #    'plot_cut': self.totalCut,
                #    'binning': '(50, 0.8, 1.2)'
                #},
                {
                        'name': 'lep2_Iso_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "({0}.isEl) ? electron_relativeIsoR03_withEA[{1}] : muon_relativeIsoR04_deltaBeta[{1}]".format(self.lep2_str, self.lep2_fwkIdx),
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 0.4)'
                },
                {
                        'name': 'jet1_eta_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".p4.Eta()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -2.5, 2.5)'
                },
                {
                        'name': 'jet1_phi_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".p4.Phi()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -3.1416, 3.1416)'
                },
                {
                        'name': 'jet2_eta_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".p4.Eta()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -2.5, 2.5)'
                },
                {
                        'name': 'jet2_phi_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".p4.Phi()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -3.1416, 3.1416)'
                },
                #{
                #        'name': 'jet1_scaleFactor_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': get_csvv2_sf(self.btagWP1, self.jet1_fwkIdx),
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0.5, 1.5)'
                #},
                #{
                #        'name': 'jet2_scaleFactor_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': get_csvv2_sf(self.btagWP2, self.jet2_fwkIdx),
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0.5, 1.5)'
                #}
                {
                        'name': 'met_phi_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "met_p4.Phi()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -3.1416, 3.1416)'
                },
                {
                        'name': 'll_eta_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject + ".ll_p4.Eta()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, -5, 5)'
                },
                {
                        'name': 'jj_eta_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject + ".jj_p4.Eta()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, -5, 5)'
                },
                {
                        'name': 'll_DPhi_l_l_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".DPhi_l_l)",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                #{
                #        'name': 'll_scaleFactor_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': get_leptons_SF(self.ll_str, self.lepid1, self.lepid2, self.lepiso1, self.lepiso2, "nominal"),
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0.8, 1.2)'
                #}
                {
                        'name': 'jj_DPhi_j_j_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".DPhi_j_j)",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                #{
                #        'name': 'jj_scaleFactor_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': "{0} * {1}".format(get_csvv2_sf(self.btagWP1, self.jet1_fwkIdx), get_csvv2_sf(self.btagWP2, self.jet2_fwkIdx)),
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0.5, 1.5)'
                #} 
                #{
                #        'name': 'llmetjj_n_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': "Length$(%s)"%self.mapIndices,
                #        'plot_cut': self.totalCut,
                #        'binning': '(18, 0, 18)'
                #},
                {
                        'name': 'llmetjj_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 250)'
                },
                {
                        'name': 'llmetjj_DPhi_ll_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".DPhi_ll_met)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                },
                #{
                #        'name': 'llmetjj_minDPhi_l_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': self.baseObject+".minDPhi_l_met",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0, 3.1416)'
                #},
                #{
                #        'name': 'llmetjj_maxDPhi_l_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': self.baseObject+".maxDPhi_l_met",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0, 3.1416)'
                #},
                #{
                #        'name': 'llmetjj_MT_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': self.baseObject+".MT", # ll[ill].p4 + met[imet].p4).M()
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0, 600)'
                #},
                #{
                #        'name': 'llmetjj_projMET_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': "abs("+self.baseObject+".projectedMet)",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0, 400)'
                #},
                {
                        'name': 'llmetjj_DPhi_jj_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".DPhi_jj_met)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                },
                {
                        'name': 'llmetjj_minDPhi_j_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".minDPhi_j_met",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name': 'llmetjj_maxDPhi_j_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".maxDPhi_j_met",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                #{
                #        'name': 'llmetjj_maxDR_l_j_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': self.baseObject+".maxDR_l_j",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0, 6)'
                #},
                #{
                #        'name': 'llmetjj_DR_ll_jj_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': self.baseObject+".DR_ll_jj",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0, 6)'
                #},
                #{
                #        'name': 'llmetjj_DR_llmet_jj_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': self.baseObject+".DR_llmet_jj",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0, 6)'
                #},
                #{
                #        'name': 'llmetjj_DPhi_llmet_jj_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': "abs("+self.baseObject+".DPhi_llmet_jj)",
                #        'plot_cut': self.totalCut,
                #        'binning': '(25, 0, 3.1416)'
                #},
                # {
                        # 'name': 'llmetjj_cosThetaStar_CS_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        # 'variable': "abs("+self.baseObject+".cosThetaStar_CS)",
                        # 'plot_cut': self.totalCut,
                        # 'binning': '(25, 0, 1)'
                # },
                {
                        'name': 'lljj_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".lljj_p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 500)'
                },
                {
                        'name': 'lljj_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".lljj_p4.M()",
                        'plot_cut': self.totalCut,
                        'binning': '(75, 0, 1000)'
                }
            ])
            
            # gen level plots for jj 
            #for elt in self.plots_jj:
            #    tempPlot = copy.deepcopy(elt)
            #    if "p4" in tempPlot["variable"]:
            #        tempPlot["variable"] = tempPlot["variable"].replace(self.jj_str,"hh_gen_BB")
            #        tempPlot["name"] = "gen"+tempPlot["name"]
            #        self.plots_gen.append(tempPlot)
            self.gen_plot.extend([
                {
                    'name': 'gen_mHH',
                    'variable': 'hh_gen_mHH',
                    'plot_cut': self.totalCut,
                    'binning': '(50, 0, 1200)'
                },
                {
                    'name': 'gen_costhetastar',
                    'variable': 'hh_gen_costhetastar',
                    'plot_cut': self.totalCut,
                    'binning': '(50, -1, 1)'
                },
                {
                    'name': 'gen_sample_weight',
                    'variable': '__sample_weight',
                    'plot_cut': self.totalCut,
                    'binning': '(200, -10, 10)'
                },
            ])
            
            self.evt_plot.extend([ # broken if we do not use maps
                #{
                #    'name': 'nLeptonsL_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #    'variable': "hh_nLeptonsL",
                #    'plot_cut': self.totalCut,
                #    'binning': '(6, 0, 6)'
                #},
                #{
                #    'name': 'nLeptonsT_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #    'variable': "hh_nLeptonsT",
                #    'plot_cut': self.totalCut,
                #    'binning': '(6, 0, 6)'
                #},
                #{
                #    'name': 'nMuonsL_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #    'variable': "hh_nMuonsL",
                #    'plot_cut': self.totalCut,
                #    'binning': '(5, 0, 5)'
                #},
                #{
                #    'name': 'nMuonsT_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #    'variable': "hh_nMuonsT",
                #    'plot_cut': self.totalCut,
                #    'binning': '(5, 0, 5)'
                #},
                #{
                #    'name': 'nElectronsL_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #    'variable': "hh_nElectronsL",
                #    'plot_cut': self.totalCut,
                #    'binning': '(5, 0, 5)'
                #},
                #{
                #    'name': 'nElectronsT_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #    'variable': "hh_nElectronsT",
                #    'plot_cut': self.totalCut,
                #    'binning': '(5, 0, 5)'
                #},
                {
                    'name': 'nJetsL_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "hh_nJetsL",
                    'plot_cut': self.totalCut,
                    'binning': '(8, 2, 10)'
                },
                #{
                #    'name': 'nBJetsL_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #    'variable': "hh_nBJetsL",
                #    'plot_cut': self.totalCut,
                #    'binning': '(6, 0, 6)'
                #},
                #{
                #    'name': 'nBJetsM_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #    'variable': "hh_nBJetsL",
                #    'plot_cut': self.totalCut,
                #    'binning': '(6, 0, 6)'
                #}
                ])
#                {
#                    'name': 'nLepAll_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.jjIDCat, self.jjBtagCat, self.suffix),
#                    'variable': "hh_nLeptons",
#                    'plot_cut': self.totalCut,
#                    'binning': '(5, 2, 7)'
#                },
#                {
#                    'name': 'nElAll_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.jjIDCat, self.jjBtagCat, self.suffix),
#                    'variable': "hh_nElectrons",
#                    'plot_cut': self.totalCut,
#                    'binning': '(6, 0, 6)'
#                },
#                {
#                    'name': 'nMuAll_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.jjIDCat, self.jjBtagCat, self.suffix),
#                    'variable': "hh_nMuons",
#                    'plot_cut': self.totalCut,
#                    'binning': '(6, 0, 6)'
#                },
#                {
#                    'name': 'nJet_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
#                    'variable': "Length$(%s)"%self.jetMapIndices,
#                    'plot_cut': self.totalCut,
#                    'binning': '(5, 2, 7)'
#                },
#                {
#                    'name': 'nJetAll_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.jjIDCat, self.jjBtagCat, self.suffix),
#                    'variable': "hh_nJets",
#                    'plot_cut': self.totalCut,
#                    'binning': '(10, 2, 12)'
#                },
#                {
#                    'name': 'nBJetLooseCSV_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.jjIDCat, self.jjBtagCat, self.suffix),
#                    'variable': "hh_nBJetsL",
#                    'plot_cut': self.totalCut,
#                    'binning': '(6, 0, 6)'
#                }
#            ])
            
            self.flavour_plot.extend([
                {
                    'name': 'gen_bb_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "%s.gen_bb"%self.baseObject,
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'gen_bl_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "%s.gen_bl"%self.baseObject,
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'gen_bc_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "%s.gen_bc"%self.baseObject,
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'gen_cc_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "%s.gen_cc"%self.baseObject,
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'gen_cl_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "%s.gen_cl"%self.baseObject,
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'gen_ll_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "%s.gen_ll"%self.baseObject,
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'gen_bx_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "({0}.gen_bl || {0}.gen_bc)".format(self.baseObject),
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'gen_xx_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "({0}.gen_ll || {0}.gen_cc || {0}.gen_cl)".format(self.baseObject),
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
            ])
            
            # Same as above but not symmetric (bl != lb)
            self.detailed_flavour_plot.extend([
                {
                    'name': 'gen_bb_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "({0}.gen_b && {1}.gen_b)".format(self.jet1_str, self.jet2_str),
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'gen_bc_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "({0}.gen_b && {1}.gen_c)".format(self.jet1_str, self.jet2_str),
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'gen_cb_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "({0}.gen_c && {1}.gen_b)".format(self.jet1_str, self.jet2_str),
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'gen_bl_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "({0}.gen_b && {1}.gen_l)".format(self.jet1_str, self.jet2_str),
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'gen_lb_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "({0}.gen_l && {1}.gen_b)".format(self.jet1_str, self.jet2_str),
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'gen_cc_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "({0}.gen_c && {1}.gen_c)".format(self.jet1_str, self.jet2_str),
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'gen_cl_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "({0}.gen_c && {1}.gen_l)".format(self.jet1_str, self.jet2_str),
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'gen_lc_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "({0}.gen_l && {1}.gen_c)".format(self.jet1_str, self.jet2_str),
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'gen_ll_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "({0}.gen_l && {1}.gen_l)".format(self.jet1_str, self.jet2_str),
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
            ])
            
            self.vertex_plot.append({
                        'name': 'nPV_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "vertex_n",
                        'plot_cut': self.totalCut,
                        'binning': '(40, 0, 40)'
                })
            self.genht_plot.append({
                        'name': 'gen_ht_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "event_ht",
                        'plot_cut': self.totalCut,
                        'binning': '(100, 0, 800)'
                })


            self.forSkimmer_plot.extend([
                {
                    'name': 'event_weight_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "event_weight",
                    'plot_cut': self.totalCut,
                    'binning': '(500, -10000, 10000)'
                },
                {
                    'name': 'event_pu_weight_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "event_pu_weight",
                    'plot_cut': self.totalCut,
                    'binning': '(50, 0, 6)'
                },
                {
                    'name': 'isElEl_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "%s.isElEl"%self.baseObject,
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'isMuMu_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "%s.isMuMu"%self.baseObject,
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'isElMu_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "%s.isElMu"%self.baseObject,
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'isMuEl_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "%s.isMuEl"%self.baseObject,
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name': 'event_number_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "event_event",
                    'plot_cut': self.totalCut,
                    'binning': '(300, 0, 300000)'
                },
                {
                    'name': 'event_run_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "event_run",
                    'plot_cut': self.totalCut,
                    'binning': '(300, 0, 300000)'
                },
                {
                    'name': 'isSF_%s_%s_%s%s' % (self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': self.baseObject + ".isSF",
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)',
                    'type': 'bool'
                },
            ])
            
            forSkimmer_totalWeight = "event_weight * (%s) * (%s) * (%s)" % (available_weights["llidiso"], available_weights["pu"], available_weights["trigeff"])
            if "nobtag" in self.baseObject:
                totalWeight = forSkimmer_totalWeight 
                if "dy_nobtag_to_btagM_BDT" in weights:
                    totalWeight = forSkimmer_totalWeight + " * " + available_weights["dy_nobtag_to_btagM_BDT"]
                self.forSkimmer_plot.extend([
                    {
                        'name': 'total_weight_%s_%s_%s%s' % (self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': totalWeight,
                        'plot_cut': self.totalCut,
                        'binning': '(5, -2, 2)'
                    }
                ])
            else:
                totalWeight = forSkimmer_totalWeight + " * (%s) * (%s)" % (available_weights["jjbtag_heavy"], available_weights["jjbtag_light"])
                self.forSkimmer_plot.extend([
                    {
                        'name': 'total_weight_%s_%s_%s%s' % (self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': totalWeight,
                        'plot_cut': self.totalCut,
                        'binning': '(5, -2, 2)'
                    }
                ])
        


        plotsToReturn = []
        
        for plotFamily in requested_plots:
            
            if "scale" in systematic:

                # will fail if we can't find the scale index
                scaleIndex = str(int(systematic[-1]))
                
                scaleWeight = "event_scale_weights[%s]" % scaleIndex
                
                for plot in getattr(self, plotFamily + "_plot"):
                    # Two different ways to normalise the variations
                    if "Uncorr" not in systematic:
                        # The normalisation is never applied on data, so we're safe even when applying DY reweighting
                        plot["normalize-to"] = "scale_%s" % scaleIndex
                    if not "Weight" in plotFamily:
                        # Be careful to use 1 for data when applying DY reweighting
                        plot["weight"] = "event_weight" + " * (runOnMC ? " + scaleWeight + " : 1. )"
                        for weight in weights:
                            plot["weight"] += " * " + available_weights[weight]
                    else:
                        print "No other weight than event_weight for ", plotFamily 
                    plotsToReturn.append(plot)
                
            elif "pdf" in systematic:
                
                for plot in getattr(self, plotFamily + "_plot"):
                    if not "Weight" in plotFamily:
                        # Be careful to use 1 for data when applying DY reweighting
                        plot["weight"] = "event_weight" + " * (runOnMC ? " + pdfWeight + " : 1.)"
                        # The normalisation is never applied on data, so we're safe even when applying DY reweighting
                        plot["normalize-to"] = normalization
                        for weight in weights:
                            plot["weight"] += " * " + available_weights[weight]
                    else:
                        print "No other weight than event_weight for ", plotFamily 
                    plotsToReturn.append(plot)
            
            else:
                
                for plot in getattr(self, plotFamily + "_plot"):
                    if not "Weight" in plotFamily and "sample_weight" not in plot["name"]:
                        plot["weight"] = "event_weight"
                        # The normalisation is never applied on data, so we're safe even when applying DY reweighting
                        plot["normalize-to"] = normalization
                        for weight in weights:
                            plot["weight"] += " * " + available_weights[weight]
                    else:
                        # Divide by sample_weight since we cannot avoid it in histFactory
                        plot["weight"] = "event_weight/__sample_weight"
                        print "No other weight than event_weight for ", plotFamily 
                    plotsToReturn.append(plot)

        # If requested, do NOT force weights to 1 for data
        if allowWeightedData:
            for plot in plotsToReturn:
                plot["allow-weighted-data"] = True

        # Remove possible duplicates (same name => they would be overwritten when saving the output file anyway)
        cleanedPlotList = []
        checkedNames = []
        for p in plotsToReturn:
            if p["name"] not in checkedNames:
                checkedNames.append(p["name"])
                cleanedPlotList.append(p)
        if len(plotsToReturn) - len(cleanedPlotList) < 0:
            print("Warning: removed {} duplicate plots!".format(-len(plotsToReturn) + len(cleanedPlotList)))

        return cleanedPlotList


    def joinCuts(self, *cuts):
        if len(cuts) == 0:
            return ""
        elif len(cuts) == 1:
            return cuts[0]
        else:
            totalCut = "("
            for cut in cuts:
                cut = cut.strip().strip("&")
                if cut == "":
                    continue
                totalCut += "(" + cut + ")&&" 
            totalCut = totalCut.strip("&") + ")"
            return totalCut

