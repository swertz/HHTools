import copy, sys, os
import numpy as np

# Bunch of flags
use_lwtnn = True
use_keras = True

def get_scram_tool_info(tool, tag):
    import subprocess

    cmd = ['scram', 'tool', 'tag', tool, tag]

    return subprocess.check_output(cmd).strip()

def default_code_before_loop():
    return r"""
        // DY reweighting
        
        // "binned" in mll: below peak, peak, above peak
        auto get_mll_bin = [](float mll) -> std::size_t {
            if (mll < 76)
                return 0;
            else if (mll > 106)
                return 2;
            return 1;
        };
        std::array<FWBTagEfficiencyOnBDT, 3> fwBtagEff {
            FWBTagEfficiencyOnBDT("/nfs/scratch/fynu/swertz/CMSSW_8_0_25/src/cp3_llbb/HHTools/DYEstimation/170311_btag_efficiency_systematics/btagging_efficiency.root", "/nfs/scratch/fynu/swertz/CMSSW_8_0_25/src/cp3_llbb/HHTools/DYEstimation/170311_btag_efficiency_systematics/btagging_scale_factors.root", "/nfs/scratch/fynu/swertz/CMSSW_8_0_25/src/cp3_llbb/HHTools/DYEstimation/170311_bb_cc_vs_rest_10var_dyFlavorFractions_systematics/mll_cut/flavour_fractions.root"),
            FWBTagEfficiencyOnBDT("/nfs/scratch/fynu/swertz/CMSSW_8_0_25/src/cp3_llbb/HHTools/DYEstimation/170311_btag_efficiency_systematics/btagging_efficiency.root", "/nfs/scratch/fynu/swertz/CMSSW_8_0_25/src/cp3_llbb/HHTools/DYEstimation/170311_btag_efficiency_systematics/btagging_scale_factors.root", "/nfs/scratch/fynu/swertz/CMSSW_8_0_25/src/cp3_llbb/HHTools/DYEstimation/170311_bb_cc_vs_rest_10var_dyFlavorFractions_systematics/mll_peak/flavour_fractions.root"),
            FWBTagEfficiencyOnBDT("/nfs/scratch/fynu/swertz/CMSSW_8_0_25/src/cp3_llbb/HHTools/DYEstimation/170311_btag_efficiency_systematics/btagging_efficiency.root", "/nfs/scratch/fynu/swertz/CMSSW_8_0_25/src/cp3_llbb/HHTools/DYEstimation/170311_btag_efficiency_systematics/btagging_scale_factors.root", "/nfs/scratch/fynu/swertz/CMSSW_8_0_25/src/cp3_llbb/HHTools/DYEstimation/170311_bb_cc_vs_rest_10var_dyFlavorFractions_systematics/mll_above_peak/flavour_fractions.root")
        };


        // DY BDT evaluation
        
        TMVAEvaluator dy_bdt_reader("/nfs/scratch/fynu/swertz/CMSSW_8_0_25/src/cp3_llbb/HHTools/DYEstimation/weights/2017_02_17_BDTDY_bb_cc_vs_rest_10var_kBDT.weights.xml", { "jet1_pt",  "jet1_eta", "jet2_pt", "jet2_eta", "jj_pt", "ll_pt", "ll_eta", "llmetjj_DPhi_ll_met", "ht", "nJetsL" });
        
        MVAEvaluatorCache<TMVAEvaluator> dy_bdt(dy_bdt_reader);

        // Keras NN evaluation
        
        // Resonant
        LWTNNEvaluator resonant_lwt_nn("/nfs/scratch/fynu/sbrochet/Moriond17/CMSSW_8_0_26_p2_HH_analysis/src/cp3_llbb/HHTools/mvaTraining/hh_resonant_trained_models/2017-03-02_260_270_300_350_400_450_500_550_600_650_750_800_900_latest_march_prod_100epochs/hh_resonant_trained_model_lwtnn.json",
            {"jj_pt", "ll_pt", "ll_M", "ll_DR_l_l", "jj_DR_j_j", "llmetjj_DPhi_ll_jj", "llmetjj_minDR_l_j", "llmetjj_MTformula", "isSF", "M_X"});

        MVAEvaluatorCache<LWTNNEvaluator> resonant_nn_evaluator(resonant_lwt_nn);

        // Non-resonant
        LWTNNEvaluator nonresonant_lwt_nn("/nfs/scratch/fynu/sbrochet/Moriond17/CMSSW_8_0_26_p2_HH_analysis/src/cp3_llbb/HHTools/mvaTraining/hh_nonresonant_trained_models/2017-03-02_latest_march_prod_100epochs/hh_nonresonant_trained_model_lwtnn.json",
            {"jj_pt", "ll_pt", "ll_M", "ll_DR_l_l", "jj_DR_j_j", "llmetjj_DPhi_ll_jj", "llmetjj_minDR_l_j", "llmetjj_MTformula", "isSF", "k_l", "k_t"});

        MVAEvaluatorCache<LWTNNEvaluator> nonresonant_nn_evaluator(nonresonant_lwt_nn);

        // Stuff to ensure we evaluate the NN only on values corresponding to the signal we're running on
        // IF we run on the signal!
        bool shouldCheckResonantSignalPoint = false;
        double resonantSignalMass;
        if (!m_dataset.is_data) {
            const std::string check = "ToHHTo2B2VTo2L2Nu_M-";
            auto start = m_dataset.db_name.find(check);
            if (start != std::string::npos) {
                shouldCheckResonantSignalPoint = true;
                start += check.size();
                std::string mass_string = m_dataset.db_name.substr(start, 3);
                resonantSignalMass = std::stod(mass_string);
            }
        }
        
        bool shouldCheckNonResonantSignalPoint = false;
        double nonResonantSignalKl, nonResonantSignalKt;
        if (!m_dataset.is_data) {
            if (m_dataset.db_name.find("ToHHTo2B2VTo2L2Nu_node_") != std::string::npos && m_dataset.sample_weight_args.size() == 4) {
                shouldCheckNonResonantSignalPoint = true;
                nonResonantSignalKl = std::stod(m_dataset.sample_weight_args[1]);
                nonResonantSignalKt = std::stod(m_dataset.sample_weight_args[2]);
            }
        }
        
        shouldCheckResonantSignalPoint = false;
        shouldCheckNonResonantSignalPoint = false;
        
        auto checkResonantSignalPoint = [shouldCheckResonantSignalPoint, shouldCheckNonResonantSignalPoint, resonantSignalMass](double m) -> bool {
            if (shouldCheckNonResonantSignalPoint)
                return false;
            if (!shouldCheckResonantSignalPoint)
                return true;
            if (std::abs(m - resonantSignalMass) < 1e-4)
                return true;
            return false;
        };
        auto checkNonResonantSignalPoint = [shouldCheckNonResonantSignalPoint, shouldCheckResonantSignalPoint, nonResonantSignalKl, nonResonantSignalKt](double kl, double kt) -> bool {
            if (shouldCheckResonantSignalPoint)
                return false;
            if (!shouldCheckNonResonantSignalPoint)
                return true;
            if ((std::abs(kl - nonResonantSignalKl) < 1e-4) && (std::abs(kt - nonResonantSignalKt) < 1e-4))
                return true;
            return false;
        };

        auto nn_reshaper = [](double nn) -> double {
            // Logarithmic, smaller alpha -> stretch more low-response end
            static double alpha = 0.2;
            static double a = log(1 + alpha) - log(alpha);
            static double b = log(alpha);
            return (log(nn + alpha) - b) / a;

            /*
            // Parabolic from 0 to alpha, linear from alpha to 1
            // Stretched such that f(alpha) = beta
            static double alpha = 0.05;
            static double beta = 0.2;
            static double a = (alpha - beta) / (alpha * alpha * (1 - alpha));
            static double b = (2 * beta - alpha - alpha * beta) / (alpha * (1 - alpha));
            if (nn < alpha)
                return a * nn * nn + b * nn;
            else
                return (1 - beta) / (1 - alpha) * (nn - alpha) + beta;*/
        };
"""

def default_code_in_loop():
    return r"""
        resonant_nn_evaluator.clear();
        nonresonant_nn_evaluator.clear();
        dy_bdt.clear();
        
        for (auto& rwgt: fwBtagEff)
            rwgt.clear_cache();
"""

def default_code_after_loop():
    return ""

def default_headers():
    return [
            "utils.h",
            "flavor_weighted_btag_efficiency_on_bdt.h",
            "KerasModelEvaluator.h",
            "TMVAEvaluator.h",
            "LWTNNEvaluator.h",
            ]

def default_include_directories(scriptDir):
    global use_lwtnn
    paths = [
            os.path.join(scriptDir, "..", "common", "include"),
            ]

    # We need numpy headers for Keras NN evaluator
    if use_keras:
        paths.append(np.get_include())

    if use_lwtnn:
        # We need eigen and lwtnn
        # lwtnn is not currenly available in a CMSSW release, so use the
        # direct path
        # FIXME: This will break as soon as the SCRAM_ARCH change. The correct
        # way to do it to bump to a CMSSW release including lwtnn and use
        # `scram tool` to get the correct path
        paths.append(get_scram_tool_info('eigen', 'INCLUDE'))
        paths.append('/cvmfs/cms.cern.ch/slc6_amd64_gcc530/external/lwtnn/1.0-oenich/include')

    return paths

def default_sources(scriptDir):
    files = [
            "utils.cc",
            "flavor_weighted_btag_efficiency_on_bdt.cc",
            "TMVAEvaluator.cc"
            ]

    if use_keras:
        files.append("KerasModelEvaluator.cc")

    if use_lwtnn:
        files.append('LWTNNEvaluator.cc')

    files = [ os.path.join(scriptDir, "..", "common", "src", f) for f in files ]

    return files

def default_libraries():
    libs = []

    if use_lwtnn:
        libs.append('lwtnn')

    return libs

def default_library_directories():
    dirs = []

    if use_lwtnn:
        # FIXME: Use scram tool once lwtnn is included into a cmssw release
        dirs.append('/cvmfs/cms.cern.ch/slc6_amd64_gcc530/external/lwtnn/1.0-oenich/lib')

    return dirs

class GridReweighting:
    def __init__(self, scriptDir):
        self.scriptDir = scriptDir

    def before_loop(self):
        path = os.path.abspath(os.path.join(self.scriptDir, "..", "common", "MatrixElements"))
        if len(path) > 125:
            raise Exception("ERROR: The path to the MatrixElements folder ({}) *must* have a length smaller than 125 characters. Sorry...".format(path))

        return r'getHHEFTReweighter("{}");'.format(path)

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
                #"/nfs/scratch/fynu/swertz/Madgraph/cmssw_madgraph_lp/pp_hh_all_MV_standalone/SubProcesses/P0_gg_hh/",
                #"/nfs/scratch/fynu/swertz/Madgraph/cmssw_madgraph_lp/pp_hh_all_MV_standalone/SubProcesses/P1_gg_hh/",
                #"/nfs/scratch/fynu/swertz/Madgraph/cmssw_madgraph_lp/pp_hh_all_MV_standalone/SubProcesses/P2_gg_hh/",
                #os.path.join(self.scriptDir, "..", "common", "MatrixElements", "pp_hh_tree_MV", "build"),
            ]

    def libraries(self):
        return [
                "libme_pp_hh_5coup.a",
                # "libhhWrapper0.a", "libhhWrapper1.a", "libhhWrapper2.a", "gfortran", "m", "quadmath",
                # "libme_pp_hh_tree_MV_standalone.a",
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
    def __init__(self, btag, objects="nominal"):
        # systematic should be jecup, jecdown, jerup or jerdown. The one for lepton, btag, etc, have to be treated with the "weight" parameter in generatePlots.py (so far)

        self.baseObjectName = "hh_llmetjj"
        self.baseObject = self.baseObjectName + "[0]"
        # For backwards compatibility with other tools:
        self.suffix = self.baseObjectName + "_HWWleptons_" + ("btagM_cmva" if btag else "nobtag_cmva")
        self.btag = btag
        self.prefix = "hh_"
        
        self.lep1_str = "hh_leptons[%s.ilep1]" % self.baseObject
        self.lep2_str = "hh_leptons[%s.ilep2]" % self.baseObject
        self.jet1_str = "hh_jets[%s.ijet1]" % self.baseObject
        self.jet2_str = "hh_jets[%s.ijet2]" % self.baseObject
        self.ll_str = "%s.ll_p4" % self.baseObject 
        self.jj_str = "%s.jj_p4" % self.baseObject
        self.met_str = "met_p4"
        self.jet_coll_str = "hh_jets"
        self.lepton_coll_str = "hh_leptons"
        self.sys_fwk = ""

        if objects != "nominal":
            self.baseObjectName = self.baseObjectName.replace("hh_", "hh_" + objects + "_")
            self.baseObject = self.baseObject.replace("hh_", "hh_" + objects + "_")
            self.prefix += objects + "_"
            self.lep1_str = self.lep1_str.replace("hh_", "hh_" + objects + "_")
            self.lep2_str = self.lep2_str.replace("hh_", "hh_" + objects + "_")
            self.jet1_str = self.jet1_str.replace("hh_", "hh_" + objects + "_")
            self.jet2_str = self.jet2_str.replace("hh_", "hh_" + objects + "_")
            self.ll_str = self.ll_str.replace("hh_", "hh_" + objects + "_")
            self.jj_str = self.jj_str.replace("hh_", "hh_" + objects + "_")
            self.jet_coll_str = self.jet_coll_str.replace("hh_", "hh_" + objects + "_")
            self.lepton_coll_str = self.lepton_coll_str.replace("hh_", "hh_" + objects + "_")
            self.sys_fwk = "_" + objects
            self.met_str = "met_" + objects + "_p4"

        # needed to get scale factors (needs to be after the object modification due to systematics)
        self.lep1_fwkIdx = self.lep1_str + ".idx"
        self.lep2_fwkIdx = self.lep2_str + ".idx"
        self.jet1_fwkIdx = self.jet1_str + ".idx"
        self.jet2_fwkIdx = self.jet2_str + ".idx"

        # Ensure we have one candidate, works also for jecup etc
        self.sanityCheck = "Length$({}) > 0".format(self.baseObjectName)
        if self.btag:
            self.sanityCheck += " && {}.btag_MM".format(self.baseObject)

        # Categories (lepton flavours)
        self.dict_cat_cut =  {
            "ElEl": "({0}.isElEl && (runOnMC || (hh_elel_fire_trigger_cut && runOnElEl)) && {1}.M() > 12)".format(self.baseObject, self.ll_str),
            "MuMu": "({0}.isMuMu && (runOnMC || (hh_mumu_fire_trigger_cut && runOnMuMu)) && {1}.M() > 12)".format(self.baseObject, self.ll_str),
            "MuEl": "(({0}.isElMu || {0}.isMuEl) && (runOnMC || ((hh_muel_fire_trigger_cut || hh_elmu_fire_trigger_cut) && runOnElMu)) && {1}.M() > 12)".format(self.baseObject, self.ll_str)
                        }
        self.dict_cat_cut["SF"] = "(" + self.dict_cat_cut["ElEl"] + "||" + self.dict_cat_cut["MuMu"] + ")"
        self.dict_cat_cut["All"] = "(" + self.dict_cat_cut["ElEl"] + "||" + self.dict_cat_cut["MuMu"] + "||" + self.dict_cat_cut["MuEl"] + ")"

        # Possible stages (selection)
        mll_cut = "({0}.M() < 91 - 15)".format(self.ll_str)
        inverted_mll_cut = "({0}.M() >= 91 - 15)".format(self.ll_str)
        mll_peak = "(std::abs({0}.M() - 91) <= 15)".format(self.ll_str)
        mll_above_peak = "({0}.M() > 91 + 15)".format(self.ll_str)

        self.dict_stage_cut = {
               "no_cut": "", 
               "mll_cut": mll_cut,
               "inverted_mll_cut": inverted_mll_cut,
               "mll_peak": mll_peak,
               "mll_above_peak": mll_above_peak,
            }


    def generatePlots(self, categories, stage, requested_plots, weights, systematic="nominal", extraString="", prependCuts=[], appendCuts=[], allowWeightedData=False, resonant_signal_grid=[], nonresonant_signal_grid=[], skimSignal2D=False): 

        # Protect against the fact that data do not have jecup collections, in the nominal case we still have to check that data have one candidate 
        sanityCheck = self.sanityCheck
        if systematic != "nominal" and not allowWeightedData:
            sanityCheck = self.joinCuts("!event_is_data", self.sanityCheck)

        cuts = self.joinCuts(*(prependCuts + [sanityCheck]))
        
        electron_1_id_cut = '({0}.isEl ? ( {0}.ele_hlt_id && !(std::abs({0}.p4.Eta()) > 1.444 && std::abs({0}.p4.Eta()) < 1.566) ) : 1)'.format(self.lep1_str)
        electron_2_id_cut = '({0}.isEl ? ( {0}.ele_hlt_id && !(std::abs({0}.p4.Eta()) > 1.444 && std::abs({0}.p4.Eta()) < 1.566) ) : 1)'.format(self.lep2_str)
        cuts = self.joinCuts(cuts, electron_1_id_cut, electron_2_id_cut)

        # Keras neural network
        keras_resonant_input_variables = '{%s, %s, %s, %s, %s, %s, %s, %s, (double) %s, (double) %%s}' % (self.jj_str + ".Pt()", self.ll_str + ".Pt()", self.ll_str + ".M()", self.baseObject + ".DR_l_l", self.baseObject + ".DR_j_j", self.baseObject + ".DPhi_ll_jj", self.baseObject + ".minDR_l_j", self.baseObject + ".MT_formula", self.baseObject + ".isSF")
        keras_nonresonant_input_variables = '{%s, %s, %s, %s, %s, %s, %s, %s, (double) %s, %%f, %%f}' % (self.jj_str + ".Pt()", self.ll_str + ".Pt()", self.ll_str + ".M()", self.baseObject + ".DR_l_l", self.baseObject + ".DR_j_j", self.baseObject + ".DPhi_ll_jj", self.baseObject + ".minDR_l_j", self.baseObject + ".MT_formula", self.baseObject + ".isSF")
        
        # Keras parameter inputs
        restricted_resonant_signals = [400, 650, 900] # For 1D plots, only select a few points
        restricted_nonresonant_signals = [ (1, 1), (5.0, 2.5), (-20, 0.5) ]

        nonresonant_grid_shift  = {
                "kl": 20,
                "kt": 0
            }

        ###########
        # Weights #
        ###########

        # Lepton ID and Iso Scale Factors
        electron_id_branch = "electron_sf_id_mediumplushltsafe_hh"
        electron_reco_branch = "electron_sf_reco_moriond17"
        muon_tracking_branch = "muon_sf_tracking"
        muon_id_branch = "muon_sf_id_tight"
        muon_iso_branch = "muon_sf_iso_tight_id_tight"
        llIdIso_sf_dict = {
                "sf_lep1_el": "{id}[{0}][0] * {reco}[{0}][0]".format(self.lep1_fwkIdx, id=electron_id_branch, reco=electron_reco_branch),
                "sf_lep2_el": "{id}[{0}][0] * {reco}[{0}][0]".format(self.lep2_fwkIdx, id=electron_id_branch, reco=electron_reco_branch),
                "sf_lep1_mu": "{tracking}[{0}][0] * {id}[{0}][0] * {iso}[{0}][0]".format(self.lep1_fwkIdx, tracking=muon_tracking_branch, id=muon_id_branch, iso=muon_iso_branch),
                "sf_lep2_mu": "{tracking}[{0}][0] * {id}[{0}][0] * {iso}[{0}][0]".format(self.lep2_fwkIdx, tracking=muon_tracking_branch, id=muon_id_branch, iso=muon_iso_branch),
                "err_lep1_el": "0.",
                "err_lep1_mu": "0.",
                "err_lep2_el": "0.",
                "err_lep2_mu": "0.",
            }
        llIdIso_var = "NOMINAL"
        
        for sf in ["elidiso", "elreco", "mutracking", "muid", "muiso"]:
            if sf in systematic:
                if "up" in systematic:
                    llIdIso_var = "UP"
                    var_index = "2"
                elif "down" in systematic:
                    llIdIso_var = "DOWN"
                    var_index = "1"
                else:
                    raise Exception("Could not find up or down variation")
                
                if sf == "elidiso":
                    llIdIso_sf_dict["err_lep1_el"] = "{id}[{0}][{1}] * {reco}[{0}][0]".format(self.lep1_fwkIdx, var_index, id=electron_id_branch, reco=electron_reco_branch)
                    llIdIso_sf_dict["err_lep2_el"] = "{id}[{0}][{1}] * {reco}[{0}][0]".format(self.lep2_fwkIdx, var_index, id=electron_id_branch, reco=electron_reco_branch)
                
                if sf == "elreco":
                    llIdIso_sf_dict["err_lep1_el"] = "{id}[{0}][0] * {reco}[{0}][{1}]".format(self.lep1_fwkIdx, var_index, id=electron_id_branch, reco=electron_reco_branch)
                    llIdIso_sf_dict["err_lep2_el"] = "{id}[{0}][0] * {reco}[{0}][{1}]".format(self.lep2_fwkIdx, var_index, id=electron_id_branch, reco=electron_reco_branch)
                
                if sf == "mutracking":
                    llIdIso_sf_dict["err_lep1_mu"] = "{tracking}[{0}][{1}] * {id}[{0}][0] * {iso}[{0}][0]".format(self.lep1_fwkIdx, var_index, tracking=muon_tracking_branch, id=muon_id_branch, iso=muon_iso_branch)
                    llIdIso_sf_dict["err_lep2_mu"] = "{tracking}[{0}][{1}] * {id}[{0}][0] * {iso}[{0}][0]".format(self.lep2_fwkIdx, var_index, tracking=muon_tracking_branch, id=muon_id_branch, iso=muon_iso_branch)
                
                if sf == "muid":
                    llIdIso_sf_dict["err_lep1_mu"] = "{tracking}[{0}][0] * {id}[{0}][{1}] * {iso}[{0}][0]".format(self.lep1_fwkIdx, var_index, tracking=muon_tracking_branch, id=muon_id_branch, iso=muon_iso_branch)
                    llIdIso_sf_dict["err_lep2_mu"] = "{tracking}[{0}][0] * {id}[{0}][{1}] * {iso}[{0}][0]".format(self.lep2_fwkIdx, var_index, tracking=muon_tracking_branch, id=muon_id_branch, iso=muon_iso_branch)
                
                if sf == "muiso":
                    llIdIso_sf_dict["err_lep1_mu"] = "{tracking}[{0}][0] * {id}[{0}][0] * {iso}[{0}][{1}]".format(self.lep1_fwkIdx, var_index, tracking=muon_tracking_branch, id=muon_id_branch, iso=muon_iso_branch)
                    llIdIso_sf_dict["err_lep2_mu"] = "{tracking}[{0}][0] * {id}[{0}][0] * {iso}[{0}][{1}]".format(self.lep2_fwkIdx, var_index, tracking=muon_tracking_branch, id=muon_id_branch, iso=muon_iso_branch)

        llIdIso_sf = """( common::combineScaleFactors<2>( {{ {{ 
                {{ 
                    ({lep1}.isEl) ? {sf_lep1_el} : {sf_lep1_mu},
                    ({lep1}.isEl) ? {err_lep1_el} : {err_lep1_mu}
                }},
                {{
                    ({lep2}.isEl) ? {sf_lep2_el} : {sf_lep2_mu},
                    ({lep2}.isEl) ? {err_lep2_el} : {err_lep2_mu}
                }}
            }} }}, common::Variation::{var} ) )""".format(lep1=self.lep1_str, lep2=self.lep2_str, var=llIdIso_var, **llIdIso_sf_dict)

        # BTAG SF, only applied if requesting b-tags
        if self.btag:
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

            jjBtag_heavyjet_sf = "(common::combineScaleFactors<2>({{ {{ {{ jet{0}_sf_cmvav2_heavyjet_{1}[{2}][0] , jet{0}_sf_cmvav2_heavyjet_{1}[{2}]{3} }}, {{ jet{0}_sf_cmvav2_heavyjet_{1}[{4}][0], jet{0}_sf_cmvav2_heavyjet_{1}[{4}]{3} }} }} }}, common::Variation::{5}) )".format(self.sys_fwk, "medium", self.jet1_fwkIdx, jjBtag_heavy_sfIdx, self.jet2_fwkIdx, jjBtag_heavy_strCommon)

            jjBtag_lightjet_sf = "(common::combineScaleFactors<2>({{ {{ {{ jet{0}_sf_cmvav2_lightjet_{1}[{2}][0] , jet{0}_sf_cmvav2_lightjet_{1}[{2}]{3} }},{{ jet{0}_sf_cmvav2_lightjet_{1}[{4}][0], jet{0}_sf_cmvav2_lightjet_{1}[{4}]{3} }} }} }}, common::Variation::{5}) )".format(self.sys_fwk, "medium", self.jet1_fwkIdx, jjBtag_light_sfIdx, self.jet2_fwkIdx, jjBtag_light_strCommon)

        else:
            jjBtag_heavyjet_sf = "1."
            jjBtag_lightjet_sf = "1."

        # PU WEIGHT
        puWeight = "event_pu_weight"
        if systematic == "puup":
            puWeight = "event_pu_weight_up"
        if systematic == "pudown":
            puWeight = "event_pu_weight_down"

        # PDF, HDAMP weight
        pdfWeight = ""
        normalization = "nominal"
        for pdf in ["", "qq", "gg", "qg"]:
            for var in ["up", "down"]:
                if systematic == "pdf" + pdf + var:
                    _pdf = pdf + "_" if pdf != "" else ""
                    pdfWeight = "event_pdf_weight_" + _pdf + var
                    normalization = "pdf_" + _pdf + var
        for var in ["up", "down"]:
            if systematic == "hdamp" + var:
                pdfWeight = "event_hdamp_weight_" + var
                normalization = "hdamp_" + var

        # TRIGGER EFFICIENCY
        trigEff = "({0}.trigger_efficiency)".format(self.baseObject)
        if systematic == "trigeffup":
            trigEff = "({0}.trigger_efficiency_upVariated)".format(self.baseObject)
        if systematic == "trigeffdown":
            trigEff = "({0}.trigger_efficiency_downVariated)".format(self.baseObject)

        # DY BDT reweighting
        # 17_02_17
        dy_bdt_variables = [
                self.jet1_str + ".p4.Pt()",
                self.jet1_str + ".p4.Eta()",
                self.jet2_str + ".p4.Pt()",
                self.jet2_str + ".p4.Eta()",
                self.jj_str + ".Pt()",
                self.ll_str + ".Pt()",
                self.ll_str + ".Eta()",
                "abs(" + self.baseObject + ".DPhi_ll_met)",
                self.prefix + "HT",
                "(double) " + self.prefix + "nJetsL",
            ]
        dy_bdt_variables_string = "{ " + ", ".join(dy_bdt_variables) + " }"
        
        dy_nobtag_to_btagM_weight_BDT = 'fwBtagEff[get_mll_bin({ll}.M())].get_cached({j1}, {j2}, dy_bdt.evaluate({bdt}), "{syst}")'.format(ll=self.ll_str, j1=self.jet1_str + ".p4", j2=self.jet2_str + ".p4", bdt=dy_bdt_variables_string, syst=systematic)

        available_weights = {
                'trigeff': trigEff,
                'jjbtag_heavy': jjBtag_heavyjet_sf,
                'jjbtag_light': jjBtag_lightjet_sf,
                'llidiso': llIdIso_sf,
                'pu': puWeight,
                'dy_nobtag_to_btagM_BDT': dy_nobtag_to_btagM_weight_BDT,
                }
        
        # Append the proper extension to the name plot if needed
        self.systematicString = ""
        if not systematic == "nominal":
            self.systematicString = "__" + systematic

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
        self.btag_efficiency_2d_plot = []

        self.other_plot = []
        self.vertex_plot = []
        self.genht_plot = []

        self.forSkimmer_plot = []
        self.event_number_plot = []

        for cat in categories:

            catCut = self.dict_cat_cut[cat]
            self.totalCut = self.joinCuts(cuts, catCut, self.dict_stage_cut[stage], *appendCuts)
            
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
            def skimSignal2DCut(*args):
                if len(args) == 1:
                    return "checkResonantSignalPoint({})".format(*args)
                if len(args) == 2:
                    return "checkNonResonantSignalPoint({}, {})".format(*args)
            
            for m in resonant_signal_grid:
                if m in restricted_resonant_signals:
                    self.resonant_nnoutput_plot.append({
                            'name': 'NN_resonant_M%d_%s_%s_%s%s' % (m, self.llFlav, self.suffix, self.extraString, self.systematicString),
                            'variable': 'nn_reshaper(resonant_nn_evaluator.evaluate(%s))' % (keras_resonant_input_variables % m),
                            'plot_cut': self.totalCut,
                            'binning': '(50, {}, {})'.format(0, 1)
                    })
                
                _cut = self.joinCuts(skimSignal2DCut(m), self.totalCut) if skimSignal2D else self.totalCut
                self.mjj_vs_resonant_nnoutput_plot.append({
                        'name': 'mjj_vs_NN_resonant_M%d_%s_%s_%s%s' % (m, self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jj_str + '.M() ::: nn_reshaper(resonant_nn_evaluator.evaluate(%s))' % (keras_resonant_input_variables % m),
                        'plot_cut': _cut,
                        'binning': '(3, { 0, 75, 140, 13000 }, 25, 0, 1)'
                })

            for point in nonresonant_signal_grid:
                kl = point[0]
                kt = point[1]
                point_str = "point_{:.2f}_{:.2f}".format(kl, kt).replace(".", "p").replace("-", "m")
                _cut = self.joinCuts(skimSignal2DCut(kl, kt), self.totalCut) if skimSignal2D else self.totalCut
                kl += nonresonant_grid_shift["kl"]
                kt += nonresonant_grid_shift["kt"]
                if point in restricted_nonresonant_signals:
                    self.nonresonant_nnoutput_plot.append({
                            'name': 'NN_nonresonant_%s_%s_%s_%s%s' % (point_str, self.llFlav, self.suffix, self.extraString, self.systematicString),
                            'variable': 'nn_reshaper(nonresonant_nn_evaluator.evaluate(%s))' % (keras_nonresonant_input_variables % (kl, kt)),
                            'plot_cut': self.totalCut,
                            'binning': '(50, {}, {})'.format(0, 1)
                    })
                self.mjj_vs_nonresonant_nnoutput_plot.append({
                        'name': 'mjj_vs_NN_nonresonant_%s_%s_%s_%s%s' % (point_str, self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jj_str + '.M() ::: nn_reshaper(nonresonant_nn_evaluator.evaluate(%s))' % (keras_nonresonant_input_variables % (kl, kt)),
                        'plot_cut': _cut,
                        'binning': '(3, { 0, 75, 140, 13000 }, 25, 0, 1)'
                })
            
            # DY reweighting plots
            # 17_02_17
            # Regular binning for plots:
            dy_bdt_flat_binning = '(50, {-0.5101676653977448, -0.3037112694618912, -0.25776621333925404, -0.22831473724254012, -0.2058976226947669, -0.18737627841862642, -0.17109101237779453, -0.1565703579397076, -0.14330560537675097, -0.1310359580150374, -0.1197784471015856, -0.10918491457907857, -0.09911075218981483, -0.08976692416038033, -0.0809107322448998, -0.07248030208546734, -0.06440158708656464, -0.05664445757506834, -0.04907888953354581, -0.04170318249950038, -0.0344922614769401, -0.0274908454765098, -0.02051556234044503, -0.01363614199605131, -0.006815197743717338, 0., 0.00860145135249569, 0.016666467134577426, 0.02408777663779528, 0.03222169904428225, 0.03964077613807283, 0.04650723992677568, 0.053785503108807996, 0.06085711547827342, 0.06764767808181676, 0.07489903876759747, 0.08197523639170723, 0.08905533336035248, 0.09649764674849821, 0.10422079837620835, 0.11189665635033663, 0.12002664935476777, 0.12849171686877514, 0.13806668191128738, 0.14732139513409487, 0.15859674959359168, 0.17097453554261796, 0.18582080656038966, 0.20358479195523596, 0.22993714767148515, 0.4})'
            # Use these special binnings only for computing Fij:
            if stage == "mll_cut":
                dy_bdt_flat_binning =  '(30, {-0.51, -0.24336378993843724, -0.19334178535513655, -0.1617002719204834, -0.13722684111510575, -0.1176740939882657, -0.10000023478454165, -0.08465874454820496, -0.07126791628951663, -0.05939533454416219, -0.04886817525318505, -0.038169394085349605, -0.028170910327335083, -0.01842442408869435, -0.009175556128479562, 0., 0.017672337607399422, 0.032772612975530156, 0.04431836038599957, 0.057366730031835365, 0.06807419443633557, 0.08060152138866084, 0.09068752149504272, 0.10617761713855838, 0.11853985824697665, 0.13331654912329943, 0.14915837795007816, 0.16842695825466836, 0.19210912647356354, 0.23254815636598256, 0.4})'
            elif stage == "mll_peak":
                dy_bdt_flat_binning = '(50, {-0.51, -0.30648147039955576, -0.26049108258184067, -0.2309395665926607, -0.20862139231464938, -0.19007051097210237, -0.1737642840929558, -0.15920207826882662, -0.14585383293640194, -0.13349257728248393, -0.12205087646867921, -0.11132629744135186, -0.10115444403168983, -0.09167042348108852, -0.08268624748142982, -0.07413327042673702, -0.06592124575539784, -0.05794120013592082, -0.05020134497665048, -0.042654049233194, -0.0353232066854666, -0.028144119539440033, -0.021044635216304564, -0.013986791007770387, -0.006988409105077877, 0., 0.008175407998005178, 0.016056370744565632, 0.023625782464709852, 0.031382989560045246, 0.03873257041686817, 0.045859664140387724, 0.052895219580672566, 0.05985075344091263, 0.06694049588333532, 0.0741468555107746, 0.08128244677706187, 0.08859804055405016, 0.0959315335989803, 0.10324717838732622, 0.11103961896255608, 0.11910942137054367, 0.12755510999157632, 0.13683100174343424, 0.14638226962067796, 0.15732762127561312, 0.169380669967978, 0.1835774386408878, 0.20096074488986812, 0.22589059373981762, 0.4})'
            elif stage == "mll_above_peak":
                dy_bdt_flat_binning = '(30, {-0.51, -0.2694119711816292, -0.21997229307491342, -0.1877386173657523, -0.16216658708508025, -0.1410157739039748, -0.12183360982330284, -0.10558126766657198, -0.08999256096557819, -0.0757172462424543, -0.06202645816308408, -0.04907084721078949, -0.036242288160678926, -0.024218895694641727, -0.012123132322284874, 0., 0.013592735003800609, 0.02447521492303922, 0.036509902193321245, 0.04740083630187158, 0.05782216837961173, 0.06977325879168576, 0.07847199090508866, 0.09029205585468365, 0.10278579164891267, 0.11598060711671343, 0.12908019021888104, 0.14702650618665358, 0.1692660223200593, 0.20190847709874246, 0.4})'
            self.dy_rwgt_bdt_plot.extend([
                {
                    'name': 'DY_BDT_flat_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': 'dy_bdt.evaluate({})'.format(dy_bdt_variables_string),
                    'plot_cut': self.totalCut,
                    'binning': dy_bdt_flat_binning,
                },
            ])
            
            def get_jet_flavour_cut(flav, jet_idx):
                if flav == "g":
                    return "{jets}[{idx}].gen_l && jet{sys}_partonFlavor[{jets}[{idx}].idx] == 21".format(sys=self.sys_fwk, jets=self.jet_coll_str, idx=jet_idx)
                elif flav == "q":
                    return "{jets}[{idx}].gen_l && std::abs(jet{sys}_partonFlavor[{jets}[{idx}].idx]) >= 1 && std::abs(jet{sys}_partonFlavor[{jets}[{idx}].idx]) <= 3".format(sys=self.sys_fwk, jets=self.jet_coll_str, idx=jet_idx)
                elif flav == "n":
                    return "{jets}[{idx}].gen_l && jet{sys}_partonFlavor[{jets}[{idx}].idx] == 0".format(sys=self.sys_fwk, jets=self.jet_coll_str, idx=jet_idx)
                else:
                    return "{jets}[{idx}].gen_{flav}".format(jets=self.jet_coll_str, idx=jet_idx, flav=flav)
            
            #for flav1 in ["b", "c", "l", "q", "g", "n"]:
            #    for flav2 in ["b", "c", "l", "q", "g", "n"]:
                    #if sorted([flav1, flav2]) in [["l", "q"], ["g", "l"], ["l", "n"]]: continue
            for flav1 in ["b", "c", "l"]:
                for flav2 in ["b", "c", "l"]:
                    self.dy_rwgt_bdt_flavour_plot.append({
                            'name': 'DY_BDT_flav_%s%s_%s_%s_%s%s' % (flav1, flav2, self.llFlav, self.suffix, self.extraString, self.systematicString),
                            'variable': 'dy_bdt.evaluate({})'.format(dy_bdt_variables_string),
                            'plot_cut': self.joinCuts(self.totalCut, get_jet_flavour_cut(flav1, self.baseObject + ".ijet1"), get_jet_flavour_cut(flav2, self.baseObject + ".ijet2")),
                            'binning': dy_bdt_flat_binning,
                        })
            
            btag_efficiency_binning = '(11, { 20, 30, 40, 50, 75, 100, 150, 200, 300, 400, 500, 4000 }, 5, 0, 2.4)'
            #for flav in ["b", "c", "l", "q", "g", "n"]:
            for flav in ["b", "c", "l"]:
                for ijet in range(5):
                    jet_present_cut = '{}.size() > {}'.format(self.jet_coll_str, ijet + 1)
                    jet_tagged_cut = '{}[{}].btag_M'.format(self.jet_coll_str, ijet)
                    self.btag_efficiency_2d_plot.extend([
                            {
                                'name': 'btag_efficiency_jet_%d_all_flav_%s_%s_%s_%s%s' % (ijet, flav, self.llFlav, self.suffix, self.extraString, self.systematicString),
                                'variable': '{0}[{1}].p4.Pt() ::: std::abs({0}[{1}].p4.Eta())'.format(self.jet_coll_str, ijet),
                                'plot_cut': self.joinCuts(jet_present_cut, get_jet_flavour_cut(flav, ijet), self.totalCut),
                                'binning': btag_efficiency_binning
                            },
                            {
                                'name': 'btag_efficiency_jet_%d_tagged_flav_%s_%s_%s_%s%s' % (ijet, flav, self.llFlav, self.suffix, self.extraString, self.systematicString),
                                'variable': '{0}[{1}].p4.Pt() ::: std::abs({0}[{1}].p4.Eta())'.format(self.jet_coll_str, ijet),
                                'plot_cut': self.joinCuts(jet_present_cut, get_jet_flavour_cut(flav, ijet), jet_tagged_cut, self.totalCut),
                                'binning': btag_efficiency_binning
                            },
                        ])


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
                        'variable': self.met_str + ".Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 500)'
                },
                {
                        'name': 'ht_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.prefix + "HT",
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
                {
                        'name': 'lljj_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "(" + self.ll_str + "+" + self.jj_str + ").M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 200, 350)'
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
            
            mll_plot_binning = '(75, 12, 252)'
            if stage == "mll_cut":
                mll_plot_binning = '(50, 12, 76)'
            elif stage == "mll_peak":
                mll_plot_binning = '(50, 76, 106)'
            elif stage == "inverted_mll_cut":
                mll_plot_binning = '(50, 76, 252)'
            self.nn_inputs_plot.extend([
                {
                        'name': 'll_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.ll_str+".M()",
                        'plot_cut': self.totalCut,
                        'binning': mll_plot_binning
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
                        'variable': self.baseObject+".MT_formula",
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
                #{
                #        'name': 'jj_DPhi_j_j_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': "abs("+self.baseObject+".DPhi_j_j)",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0, 3.1416)'
                #},
                #{
                #        'name': 'lljj_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': self.baseObject+".lljj_p4.Pt()",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0, 500)'
                #},
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
                        'variable': self.met_str + ".Phi()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -3.1416, 3.1416)'
                },
                #{
                #        'name': 'll_eta_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': self.baseObject + ".ll_p4.Eta()",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, -5, 5)'
                #},
                #{
                #        'name': 'jj_eta_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': self.baseObject + ".jj_p4.Eta()",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, -5, 5)'
                #},
                {
                        'name': 'll_DPhi_l_l_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".DPhi_l_l)",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name': 'll_DEta_l_l_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': 'abs({}.p4.Eta() - {}.p4.Eta())'.format(self.lep1_str, self.lep2_str),
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 4)'
                },
                #{
                #        'name': 'll_scaleFactor_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': get_leptons_SF(self.ll_str, self.lepid1, self.lepid2, self.lepiso1, self.lepiso2, "nominal"),
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0.8, 1.2)'
                #}
                #{
                #        'name': 'jj_DPhi_j_j_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': "abs("+self.baseObject+".DPhi_j_j)",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0, 3.1416)'
                #},
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
                #{
                #        'name': 'llmetjj_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': self.baseObject+".p4.Pt()",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0, 250)'
                #},
                #{
                #        'name': 'llmetjj_DPhi_ll_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': "abs("+self.baseObject+".DPhi_ll_met)",
                #        'plot_cut': self.totalCut,
                #        'binning': '(25, 0, 3.1416)'
                #},
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
                #{
                #        'name': 'llmetjj_DPhi_jj_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': "abs("+self.baseObject+".DPhi_jj_met)",
                #        'plot_cut': self.totalCut,
                #        'binning': '(25, 0, 3.1416)'
                #},
                #{
                #        'name': 'llmetjj_minDPhi_j_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': self.baseObject+".minDPhi_j_met",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0, 3.1416)'
                #},
                #{
                #        'name': 'llmetjj_maxDPhi_j_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': self.baseObject+".maxDPhi_j_met",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0, 3.1416)'
                #},
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
                #{
                #        'name': 'lljj_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': self.baseObject+".lljj_p4.Pt()",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0, 500)'
                #},
                #{
                #        'name': 'lljj_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': self.baseObject+".lljj_p4.M()",
                #        'plot_cut': self.totalCut,
                #        'binning': '(75, 0, 1000)'
                #}
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
            
            for flav in ["bb", "bl", "bc", "cc", "cl", "ll", "bl", "ll"]:
                self.flavour_plot.append({
                        'name': 'gen_%s_%s_%s_%s%s'%(flav, self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "%s.gen_%s" % (self.baseObject, flav),
                        'plot_cut': self.totalCut,
                        'binning': '(2, 0, 2)'
                    })
            
            # Same as above but not symmetric (bl != lb)
            for flav1 in ["b", "c", "l"]:
                for flav2 in ["b", "c", "l"]:
                    self.detailed_flavour_plot.append({
                            'name': 'gen_%s%s_%s_%s_%s%s' % (flav1, flav2, self.llFlav, self.suffix, self.extraString, self.systematicString),
                            'variable': "({0}.gen_{2} && {1}.gen_{3})".format(self.jet1_str, self.jet2_str, flav1, flav2),
                            'plot_cut': self.totalCut,
                            'binning': '(2, 0, 2)'
                        })
            
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
            self.event_number_plot.extend([
                {
                    'name': 'event_run_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "event_run",
                    'plot_cut': self.totalCut,
                    'binning': '(500, -10000, 10000)'
                },
                {
                    'name': 'event_lumi_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "event_lumi",
                    'plot_cut': self.totalCut,
                    'binning': '(500, -10000, 10000)'
                },
                {
                    'name': 'event_event_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "event_event",
                    'plot_cut': self.totalCut,
                    'binning': '(500, -10000, 10000)'
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
            
            if "scaleUncorr" in systematic or "dyScale" in systematic:

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

