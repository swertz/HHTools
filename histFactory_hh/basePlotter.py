import copy, sys

class BasePlotter:
    def __init__(self, baseObjectName = "hh_llmetjj_allTight_btagM_csv", btagWP_str = 'medium', objects = "nominal", WP = ["T", "T", "T", "T", "L", "L", "M", "M", "csv"]):
        # systematic should be jecup, jecdown, jerup or jerdown. The one for lepton, btag, etc, have to be treated with the "weight" parameter in generatePlots.py (so far)

        self.baseObject = baseObjectName+"[0]"
        self.suffix = baseObjectName
        self.btagWP_str = btagWP_str
        
        self.lep1_str = "hh_leptons[%s.ilep1]"%self.baseObject
        self.lep2_str = "hh_leptons[%s.ilep2]"%self.baseObject
        self.jet1_str = "hh_jets[%s.ijet1]"%self.baseObject
        self.jet2_str = "hh_jets[%s.ijet2]"%self.baseObject
        self.ll_str = "%s.ll_p4"%self.baseObject 
        self.jj_str = "%s.jj_p4"%self.baseObject

        if objects != "nominal":
            baseObjectName = baseObjectName.replace("hh_", "hh_"+objects+"_")
            self.lep1_str = self.lep1_str.replace("hh_", "hh_"+objects+"_")
            self.lep2_str = self.lep2_str.replace("hh_", "hh_"+objects+"_")
            self.jet1_str = self.jet1_str.replace("hh_", "hh_"+objects+"_")
            self.jet2_str = self.jet2_str.replace("hh_", "hh_"+objects+"_")
            self.ll_str = self.ll_str.replace("hh_", "hh_"+objects+"_")
            self.jj_str = self.jj_str.replace("hh_", "hh_"+objects+"_")
            self.baseObject = self.baseObject.replace("hh_", "hh_"+objects+"_")

        # needed to get scale factors (needs to be after the object modification due to systematics)
        self.lep1_fwkIdx = self.lep1_str+".idx"
        self.lep2_fwkIdx = self.lep2_str+".idx"
        self.jet1_fwkIdx = self.jet1_str+".idx"
        self.jet2_fwkIdx = self.jet2_str+".idx"

        # Ensure we have one candidate, works also for jecup etc
        self.sanityCheck = "Length$(%s)>0"%baseObjectName

    
    def generatePlots(self, categories = ["All"], stage = "cleaning_cut", requested_plots = [], weights = ['trigeff', 'jjbtag', 'llidiso', 'pu'], extraCut = "", systematic = "nominal", extraString = "", fit2DtemplatesBinning = None):

        # MVA evaluation : ugly but necessary part
        baseStringForMVA_part1 = 'evaluateMVA("/home/fynu/sbrochet/scratch/Framework/CMSSW_7_6_5/src/cp3_llbb/HHTools//mvaTraining_hh/weights/BDTNAME_kBDT.weights.xml", '
        baseStringForMVA_part2 = '{{"jj_pt", %s}, {"ll_pt", %s}, {"ll_M", %s}, {"ll_DR_l_l", %s}, {"jj_DR_j_j", %s}, {"llmetjj_DPhi_ll_jj", %s}, {"llmetjj_minDR_l_j", %s}, {"llmetjj_MTformula", %s}})' % ( self.jj_str + ".Pt()", self.ll_str + ".Pt()", self.ll_str + ".M()", self.baseObject + ".DR_l_l", self.baseObject + ".DR_j_j", self.baseObject + ".minDR_l_j", self.baseObject + ".DPhi_ll_jj", self.baseObject + ".MT_formula")
        stringForMVA = baseStringForMVA_part1 + baseStringForMVA_part2
        
        # The following will need to be modified each time the name of the BDT output changes
        bdtNameTemplate = "DATE_BDT_NODE_SUFFIX"
        
        # v1 benchmark BDTs (w/ LO DY)
        #date = "2016_05_27"
        #nodes = ["SM", "box", "5", "8", "13", "all"]
        
        # v3 benchmark BDTs (w/ NLO DY)
        date = "2016_07_05"
        nodes = ["SM", "2", "5", "6", "12"]
        #nodes = ["SM", "2"] # Chosen BDTs
        
        suffixes = ["VS_TT_DYHTonly_tW_8var"]
        BDToutputs = {}
        bdtNames = []
        BDToutputsVariable = {}
        for node in nodes:
            for suffix in suffixes:
                bdtName = bdtNameTemplate.replace("DATE", date).replace("NODE", node).replace("SUFFIX", suffix)
                bdtNames.append(bdtName)
                BDToutputsVariable[bdtName] = baseStringForMVA_part1.replace("BDTNAME", bdtName) + baseStringForMVA_part2

        # Possible stages (selection)
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

        # High-BDT stages
        for node in nodes:
            for suffix in suffixes:
                bdtName = bdtNameTemplate.replace("DATE", date).replace("NODE", node).replace("SUFFIX", suffix)
                BDToutput = baseStringForMVA_part1.replace("BDTNAME", bdtName) + baseStringForMVA_part2
                dict_stage_cut["highBDT_node_" + node] = self.joinCuts(BDToutput + ">0", mll_cut)

        # Categories (lepton flavours)
        self.dict_cat_cut =  {
            "ElEl": "({0}.isElEl && (runOnMC || hh_elel_fire_trigger_cut) && (runOnElEl || runOnMC) && {1}.M() > 12)".format(self.baseObject, self.ll_str),
            "MuMu": "({0}.isMuMu && (runOnMC || hh_mumu_fire_trigger_cut) && (runOnMuMu || runOnMC) && {1}.M() > 12)".format(self.baseObject, self.ll_str),
            "MuEl": "(({0}.isElMu || {0}.isMuEl) && (runOnMC || hh_elmu_fire_trigger_cut || hh_muel_fire_trigger_cut) && (runOnElMu || runOnMC) && {1}.M() > 12)".format(self.baseObject, self.ll_str)
                        }   
        cut_for_All_channel = "(" + self.dict_cat_cut["ElEl"] + "||" + self.dict_cat_cut["MuMu"] + "||" +self.dict_cat_cut["MuEl"] + ")"
        cut_for_SF_channel = "(" + self.dict_cat_cut["ElEl"] + "||" + self.dict_cat_cut["MuMu"] + ")"
        self.dict_cat_cut["SF"] = cut_for_SF_channel
        self.dict_cat_cut["All"] = cut_for_All_channel

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

        # BTAG SF
        jjBtag_sfIdx = "[0]"
        jjBtag_strCommon="NOMINAL"
        if systematic == "jjbtagup":
            jjBtag_sfIdx = "[2]" 
            jjBtag_strCommon="UP"
        if systematic == "jjbtagdown":
            jjBtag_sfIdx = "[1]"
            jjBtag_strCommon="DOWN"
        # propagate jecup etc to the framework objects
        sys_fwk = ""

        if "jec" in systematic or "jer" in systematic:
            sys_fwk = "_" + systematic

        jjBtag_heavyjet_sf = "(common::combineScaleFactors<2>({{{{{{ jet{0}_sf_csvv2_heavyjet_{1}[{2}][0] , jet{0}_sf_csvv2_heavyjet_{1}[{2}]{3} }}, {{ jet{0}_sf_csvv2_heavyjet_{1}[{4}][0] , jet{0}_sf_csvv2_heavyjet_{1}[{4}]{3} }}}}}}, common::Variation::{5}) )".format(sys_fwk, self.btagWP_str, self.jet1_fwkIdx, jjBtag_sfIdx, self.jet2_fwkIdx, jjBtag_strCommon)

        jjBtag_lightjet_sf = "(common::combineScaleFactors<2>({{{{{{ jet{0}_sf_csvv2_lightjet_{1}[{2}][0] , jet{0}_sf_csvv2_lightjet_{1}[{2}]{3} }}, {{ jet{0}_sf_csvv2_lightjet_{1}[{4}][0] , jet{0}_sf_csvv2_lightjet_{1}[{4}]{3} }}}}}}, common::Variation::{5}) )".format(sys_fwk, self.btagWP_str, self.jet1_fwkIdx, jjBtag_sfIdx, self.jet2_fwkIdx, jjBtag_strCommon)

        # PU WEIGHT
        puWeight = "event_pu_weight"
        if systematic == "puup":
            puWeight = "event_pu_weight_up"
        if systematic == "pudown":
            puWeight = "event_pu_weight_down"

        # PDF weight
        pdfWeight = ""
        normalization = "nominal"
        if systematic == "pdfup" : # do not change the name of "pdfup", use latter for the proper normalization
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
        # Include dZ filter efficiency for ee and mumu
        trigEff += "*(({0}.isElEl && runOnMC) ? 0.995 : 1)".format(self.baseObject)
        trigEff += "*(({0}.isMuMu && runOnMC) ? 0.95 : 1)".format(self.baseObject)

        # Append the proper extension to the name plot if needed (scale name are down at the end of the code)
        self.systematicString = ""
        if not systematic == "nominal" and not "scale" in systematic:
            self.systematicString = "__" + systematic

        dy_high_to_low_mll_weight = "dyReweighter.getWeight(%s, %s)" % (self.lep1_str + ".p4", self.lep2_str + ".p4")
        nobtag_to_btagM_weight = "btagEff.get(%s) * btagEff.get(%s)" % (self.jet1_str + ".p4", self.jet2_str + ".p4")

        available_weights = {'trigeff' : trigEff, 'jjbtag_heavy' : jjBtag_heavyjet_sf, 'jjbtag_light': jjBtag_lightjet_sf, 'llidiso' : llIdIso_sf, 'pu' : puWeight,
                'dy_high_to_low_mll': dy_high_to_low_mll_weight,
                'nobtag_to_btagM': nobtag_to_btagM_weight}

        #########
        # PLOTS #
        #########
        self.basic_plot = []
        self.csv_plot = []
        self.bdtinput_plot = []
        self.cleancut_plot = []
        self.drllcut_plot = []
        self.drjjcut_plot = []
        self.dphilljjcut_plot = []
        self.isElEl_plot = []
        self.mll_plot = []
        self.mjj_plot = []
        self.bdtoutput_plot = []
        self.mjj_vs_bdt_plot = []

        self.flavour_plot = []

        self.llidisoWeight_plot = []
        self.mumuidisoWeight_plot = []
        self.elelidisoWeight_plot = []
        self.jjbtagWeight_plot = []
        self.trigeffWeight_plot = []
        self.puWeight_plot = []
        self.scaleWeight_plot = []
        self.pdfWeight_plot = []
        self.gen_plot = []
        self.evt_plot = []

        self.other_plot = []
        self.vertex_plot = []
        self.ht_plot = []

        self.btagging_eff_plot = []

        self.forSkimmer_plot = []

        # Protect against the fact that data do not have jecup collections, in the nominal case we still have to check that data have one candidate 
        sanityCheck = self.sanityCheck
        if systematic != "nominal":
            sanityCheck = self.joinCuts("!event_is_data", self.sanityCheck)

        for cat in categories:

            catCut = self.dict_cat_cut[cat]
            self.totalCut = self.joinCuts(sanityCheck, catCut, extraCut, dict_stage_cut[stage])
            self.llFlav = cat
            self.extraString = stage + extraString

            self.mll_plot.append({
                        'name': 'll_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.ll_str+".M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 10, 250)'
                })
            self.mjj_plot.append({
                        'name': 'jj_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jj_str+".M()",
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
            
            # BDT output plots
            for bdtName in bdtNames:
                bdtRange = (-0.6, 0.6) # default BDT range
                # Special BDT ranges
                if "BDT_SM" in bdtName: bdtRange = (-0.5, 0.5)
                if "BDT_2" in bdtName: bdtRange = (-0.5, 0.6)

                self.bdtoutput_plot.append({
                        'name': 'MVA_%s_%s_%s_%s%s' % (bdtName, self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': BDToutputsVariable[bdtName],
                        'plot_cut': self.totalCut,
                        'binning': '(50, {}, {})'.format(bdtRange[0], bdtRange[1])
                })
                
                # 2D templates: different binnings

                if fit2DtemplatesBinning is None: continue

                for binName, binning in fit2DtemplatesBinning.items():

                    self.mjj_vs_bdt_plot.append({
                            'name': 'jj_M_vs_MVA_%s_%s_%s_%s_%s%s' % (binName, bdtName, self.llFlav, self.suffix, self.extraString, self.systematicString),
                            'variable': self.jj_str + ".M() ::: " + BDToutputsVariable[bdtName],
                            'plot_cut': self.totalCut,
                            'binning': '(%s, %s, %s, %s)' % (binning["mjjBinning"], binning["bdtNbins"], bdtRange[0], bdtRange[1])
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
            self.dyWeight_plot = [
                        {'name': 'dy_reweighting_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString,  self.systematicString), 'variable': available_weights["dy_high_to_low_mll"],
                        'plot_cut': self.totalCut, 'binning': '(100, 0, 4)', 'weight': 'event_weight'}]
            self.twoBEff_plot = [
                        {'name': 'two_b_efficiency_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString,  self.systematicString), 'variable': available_weights["nobtag_to_btagM"],
                        'plot_cut': self.totalCut, 'binning': '(100, 0, 4)', 'weight': 'event_weight'}]

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
                        'binning': '(50, 15, 400)'
                },
                {
                        'name': 'lep2_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.lep2_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 10, 200)'
                },
                {
                        'name': 'lep1_pt_vs_lep2_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "%s:::%s" % (self.lep1_str+".p4.Pt()", self.lep2_str + ".p4.Pt()"),
                        'plot_cut': self.totalCut,
                        'binning': '(20, 15, 400, 20, 10, 200)'
                },
                {
                        'name': 'jet1_pt_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 20, 400)'
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
                        'binning': '(50, 0, 450)'
                }
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
            self.cleancut_plot.extend([
                #{
                #        'name': 'll_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': self.ll_str+".M()",
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0, 250)'
                #},
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
                }
            ])
            self.drllcut_plot.append(
                {
                        'name': 'll_DR_l_l_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".DR_l_l",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                })
            self.drjjcut_plot.append(
                {
                        'name': 'jj_DR_j_j_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".DR_j_j",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                })
            self.dphilljjcut_plot.append(
                {
                        'name': 'llmetjj_DPhi_ll_jj_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".DPhi_ll_jj)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                })

            self.bdtinput_plot.extend([
                {
                        'name': 'll_M_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.ll_str+".M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 10, 250)'
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
                # {
                        # 'name': 'jet1_JP_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        # 'variable': self.jet1_str+".JP",
                        # 'plot_cut': self.totalCut,
                        # 'binning': '(50, 0, 3.5)'
                # },
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
                # {
                        # 'name': 'jet2_JP_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        # 'variable': self.jet2_str+".JP",
                        # 'plot_cut': self.totalCut,
                        # 'binning': '(50, 0, 3.5)'
                # },
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
                # {
                        # 'name': 'jj_CSVprod_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        # 'variable': self.jet1_str+".CSV * " + self.jet2_str+".CSV",
                        # 'plot_cut': self.totalCut,
                        # 'binning': '(25, 0, 1)'
                # },
                # {
                        # 'name': 'jj_CSVsum_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        # 'variable': self.jet1_str+".CSV + " + self.jet2_str+".CSV",
                        # 'plot_cut': self.totalCut,
                        # 'binning': '(25, 0, 2)'
                # },
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
                # {
                        # 'name': 'llmetjj_DPhi_ll_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        # 'variable': "abs("+self.baseObject+".DPhi_ll_met)",
                        # 'plot_cut': self.totalCut,
                        # 'binning': '(25, 0, 3.1416)'
                # },
                # {
                        # 'name': 'llmetjj_minDPhi_l_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        # 'variable': self.baseObject+".minDPhi_l_met",
                        # 'plot_cut': self.totalCut,
                        # 'binning': '(50, 0, 3.1416)'
                # },
                # {
                        # 'name': 'llmetjj_maxDPhi_l_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        # 'variable': self.baseObject+".maxDPhi_l_met",
                        # 'plot_cut': self.totalCut,
                        # 'binning': '(50, 0, 3.1416)'
                # },
                {
                        'name': 'llmetjj_MT_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".MT", # ll[ill].p4 + met[imet].p4).M()
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 600)'
                },
                # {
                        # 'name': 'llmetjj_projMET_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        # 'variable': "abs("+self.baseObject+".projectedMet)",
                        # 'plot_cut': self.totalCut,
                        # 'binning': '(50, 0, 400)'
                # },
                # {
                        # 'name': 'llmetjj_DPhi_jj_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        # 'variable': "abs("+self.baseObject+".DPhi_jj_met)",
                        # 'plot_cut': self.totalCut,
                        # 'binning': '(25, 0, 3.1416)'
                # },
                # {
                        # 'name': 'llmetjj_minDPhi_j_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        # 'variable': self.baseObject+".minDPhi_j_met",
                        # 'plot_cut': self.totalCut,
                        # 'binning': '(50, 0, 3.1416)'
                # },
                # {
                        # 'name': 'llmetjj_maxDPhi_j_met_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        # 'variable': self.baseObject+".maxDPhi_j_met",
                        # 'plot_cut': self.totalCut,
                        # 'binning': '(50, 0, 3.1416)'
                # },
                {
                        'name': 'llmetjj_maxDR_l_j_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".maxDR_l_j",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name': 'llmetjj_DR_ll_jj_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".DR_ll_jj",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name': 'llmetjj_DR_llmet_jj_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".DR_llmet_jj",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name': 'llmetjj_DPhi_llmet_jj_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".DPhi_llmet_jj)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                },
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
                {
                    'name': 'nLeptonsL_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "hh_nLeptonsL",
                    'plot_cut': self.totalCut,
                    'binning': '(6, 0, 6)'
                },
                {
                    'name': 'nLeptonsT_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "hh_nLeptonsT",
                    'plot_cut': self.totalCut,
                    'binning': '(6, 0, 6)'
                },
                {
                    'name': 'nMuonsL_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "hh_nMuonsL",
                    'plot_cut': self.totalCut,
                    'binning': '(5, 0, 5)'
                },
                {
                    'name': 'nMuonsT_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "hh_nMuonsT",
                    'plot_cut': self.totalCut,
                    'binning': '(5, 0, 5)'
                },
                {
                    'name': 'nElectronsL_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "hh_nElectronsL",
                    'plot_cut': self.totalCut,
                    'binning': '(5, 0, 5)'
                },
                {
                    'name': 'nElectronsT_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "hh_nElectronsT",
                    'plot_cut': self.totalCut,
                    'binning': '(5, 0, 5)'
                },
                {
                    'name': 'nJetsL_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "hh_nJetsL",
                    'plot_cut': self.totalCut,
                    'binning': '(10, 0, 10)'
                },
                {
                    'name': 'nBJetsL_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "hh_nBJetsL",
                    'plot_cut': self.totalCut,
                    'binning': '(6, 0, 6)'
                },
                {
                    'name': 'nBJetsM_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "hh_nBJetsL",
                    'plot_cut': self.totalCut,
                    'binning': '(6, 0, 6)'
                }
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
            self.vertex_plot.append({
                        'name': 'nPV_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "vertex_n",
                        'plot_cut': self.totalCut,
                        'binning': '(40, 0, 40)'
                })
            self.ht_plot.append({
                        'name': 'ht_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
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
                    'name': 'total_weight_%s_%s_%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "event_weight * (%s) * (%s) * (%s) * (%s) * (%s)"%(available_weights["jjbtag_heavy"], available_weights["jjbtag_light"], available_weights["llidiso"], available_weights["pu"], available_weights["trigeff"]),
                    'plot_cut': self.totalCut,
                    'binning': '(5, -2, 2)'
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
                }
            ])

        plotsToReturn = []
        
        for plotFamily in requested_plots:
            
            if "scale" in systematic:
                
                scaleIndices = ["0", "1", "2", "3", "4", "5"]
                
                for scaleIndice in scaleIndices:
                    
                    scaleWeight = "event_scale_weights[%s]" % scaleIndice
                    
                    for plot in getattr(self, plotFamily+"_plot"):
                        tempPlot = copy.deepcopy(plot)
                        # Two different ways to normalise the variations
                        if "Uncorr" not in systematic:
                            tempPlot["normalize-to"] = "scale_%s" % scaleIndice
                        tempPlot["name"] += "__" + systematic + scaleIndice
                        if not "Weight" in plotFamily:
                            tempPlot["weight"] = "event_weight" + " * " + scaleWeight
                            for weight in weights:
                                tempPlot["weight"] += " * " + available_weights[weight]
                        else:
                            print "No other weight than event_weight for ", plotFamily 
                        plotsToReturn.append(tempPlot)
            
            elif "pdf" in systematic:
                
                for plot in getattr(self, plotFamily+"_plot"):
                    if not "Weight" in plotFamily:
                        plot["weight"] = "event_weight" + " * " + pdfWeight
                        plot["normalize-to"] = normalization
                        for weight in weights:
                            plot["weight"] += " * " + available_weights[weight]
                    else:
                        print "No other weight than event_weight for ", plotFamily 
                    plotsToReturn.append(plot)
            
            else:
                
                for plot in getattr(self, plotFamily+"_plot"):
                    if not "Weight" in plotFamily and "sample_weight" not in plot["name"]:
                        plot["weight"] = "event_weight"
                        plot["normalize-to"] = normalization
                        for weight in weights:
                            plot["weight"] += " * " + available_weights[weight]
                    else:
                        # Divide by sample_weight since we cannot avoid it in histFactory
                        plot["weight"] = "event_weight/__sample_weight"
                        print "No other weight than event_weight for ", plotFamily 
                    plotsToReturn.append(plot)

        return plotsToReturn


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

