import copy, sys
from HHAnalysis import HH
from ScaleFactors import *


class BasePlotter:
    def __init__(self, mode = "custom", baseObjectName = "hh_llmetjj_allTight_btagM_csv", systematic = "nominal", WP = ["T", "T", "T", "T", "L", "L", "M", "M", "csv"]):
        # mode can be "custom" or "map", if you are in map mode you need to modify baseObjectName and specify a WP
        # systematic should be jecup, jecdown, jerup or jerdown. The one for lepton, btag, etc, have to be treated with the "weight" parameter in generatePlots.py (so far)

        if mode == "map" :
            lepid1 = getattr(HH.lepID, WP[0])
            lepiso1 = getattr(HH.lepIso, WP[1])
            lepid2 = getattr(HH.lepID, WP[2])
            lepiso2 = getattr(HH.lepIso, WP[3])
            jetid1 = getattr(HH.jetID, WP[4])
            jetid2 = getattr(HH.jetID, WP[5])
            btagWP1 = getattr(HH.btagWP, WP[6])
            btagWP2 = getattr(HH.btagWP, WP[7])
            pair = getattr(HH.jetPair, WP[8])

            map = "hh_map_llmetjj"
            mapWP = HH.leplepIDIsojetjetIDbtagWPPair(lepid1, lepiso1, lepid2, lepiso2, jetid1, jetid2, btagWP1, btagWP2, pair)
            mapIndices = "%s[%s]"%(map, mapWP)
            self.baseObject = "%s[%s[0]]"%(baseObjectName, mapIndices)
            self.sanityCheck = "Length$(%s)>0"%mapIndices # ensure to have an entry in the map

            llIsoCat = HH.lepIso.map.at(lepiso1)+HH.lepIso.map.at(lepiso2) # This is to extract string from WP
            llIDCat = HH.lepID.map.at(lepid1)+HH.lepID.map.at(lepid2)
            jjIDCat = HH.jetID.map.at(jetid1)+HH.jetID.map.at(jetid2)
            jjBtagCat = HH.btagWP.map.at(btagWP1)+HH.btagWP.map.at(btagWP2)
            order = HH.jetPair.map.at(pair)
            self.suffix = 'lepIso_%s_lepID_%s_jetID_%s_btag_%s_order_%s'%(llIsoCat, llIDCat, jjIDCat, jjBtagCat, order)

            # Deprecated (but may be useful at some point)
            lepMap = "hh_map_l"
            jetMap = "hh_map_j"
            lepMapWP = HH.lepIDIso(lepid1, lepiso1)
            jetMapWP = btagWP1 # To Be Updated once jet map includes jetID
            lepMapIndices = "%s[%s]"%(lepMap, lepMapWP)
            jetMapIndices = "%s[%s]"%(jetMap, jetMapWP)

        elif mode == "custom" :
            self.baseObject = baseObjectName+"[0]"
            self.sanityCheck = "Length$(%s)>0"%baseObjectName
            self.suffix = baseObjectName

        else : 
            print "Mode has to be 'custom' or 'map'"
            sys.exit()

        self.lep1_str = "hh_leptons[%s.ilep1]"%self.baseObject
        self.lep2_str = "hh_leptons[%s.ilep2]"%self.baseObject
        self.jet1_str = "hh_jets[%s.ijet1]"%self.baseObject
        self.jet2_str = "hh_jets[%s.ijet2]"%self.baseObject
        self.ll_str = "hh_ll[%s.ill]"%self.baseObject 
        self.jj_str = "hh_jj[%s.ijj]"%self.baseObject

        # needed to plot iso variables
        self.lep1_fwkIdx = self.lep1_str+".idx"
        self.lep2_fwkIdx = self.lep2_str+".idx"
        self.jet1_fwkIdx = self.jet1_str+".idx"
        self.jet2_fwkIdx = self.jet2_str+".idx"

        self.systematicString = ""
        if systematic != "nominal" :
            self.lep1_str = self.lep1_str.replace("hh_", "hh_"+systematic+"_")
            self.lep2_str = self.lep2_str.replace("hh_", "hh_"+systematic+"_")
            self.jet1_str = self.jet1_str.replace("hh_", "hh_"+systematic+"_")
            self.jet2_str = self.jet2_str.replace("hh_", "hh_"+systematic+"_")
            self.ll_str = self.ll_str.replace("hh_", "hh_"+systematic+"_")
            self.jj_str = self.jj_str.replace("hh_", "hh_"+systematic+"_")
            self.baseObject = self.baseObject.replace("hh_", "hh_"+systematic+"_")
            self.systematicString = "__"+systematic

    def generatePlots(self, dict_cat_cut = {}, extraCut = "", extraString = "_noCut", weightsToPlot = {}):

        self.plots_lep = []
        self.plots_jet = []
        self.plots_met = []
        self.plots_ll = []
        self.plots_jj = []
        self.plots_llmetjj = []
        self.plots_gen = []
        self.plots_evt = []
        self.plots_weights = []
        self.plots_mva = []
        self.crucial_plots = []

        self.forSkimmer = []

        for cat in dict_cat_cut.keys() :

            catCut = dict_cat_cut[cat]
            self.totalCut = self.joinCuts(self.sanityCheck, catCut, extraCut)
            self.llFlav = cat
            self.extraString = extraString

            self.crucial_plots.extend([
                {
                        'name':  'lep1_pt_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.lep1_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 300)'
                },
                {
                        'name':  'lep2_pt_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.lep2_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 100)'
                },
                {
                        'name':  'jet1_pt_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 300)'
                },
                {
                        'name':  'jet1_CSV_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".CSV",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 1)'
                },
                {
                        'name':  'jet2_pt_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 250)'
                },
                {
                        'name':  'jet2_CSV_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".CSV",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 1)'
                },
                {
                        'name':  'met_pt_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "met_p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 400)'
                },
                {
                        'name':  'll_M_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.ll_str+".p4.M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 250)'
                },
                {
                        'name':  'll_pt_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.ll_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 400)'
                },
                {
                        'name':  'll_DR_l_l_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.ll_str+".DR_l_l",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'jj_M_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jj_str+".p4.M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 600)'
                },
                {
                        'name':  'jj_pt_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jj_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 400)'
                },
                {
                        'name':  'jj_DR_j_j_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jj_str+".DR_j_j",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'llmetjj_minDR_l_j_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".minDR_l_j",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'llmetjj_MTformula_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".MT_formula", # std::sqrt(2 * ll[ill].p4.Pt() * met[imet].p4.Pt() * (1-std::cos(dphi)));
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 500)'
                },
                {
                        'name':  'llmetjj_DPhi_ll_jj_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".DPhi_ll_jj)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                }
            ])

            self.plots_lep.extend([
                {
                    'name':  'lep1_pt_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': self.lep1_str+".p4.Pt()",
                    'plot_cut': self.totalCut,
                    'binning': '(50, 0, 300)'
                },
                {
                    'name':  'lep1_eta_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': self.lep1_str+".p4.Eta()",
                    'plot_cut': self.totalCut,
                    'binning': '(25, -2.5, 2.5)'
                },
                {
                    'name':  'lep1_phi_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': self.lep1_str+".p4.Phi()",
                    'plot_cut': self.totalCut,
                    'binning': '(25, -3.1416, 3.1416)'
                },
                #{
                #    'name':  'lep1_scaleFactor_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #    'variable': get_lepton_SF(self.lep1_str, self.lepid1, self.lepiso1, "nominal"),
                #    'plot_cut': self.totalCut,
                #    'binning': '(50, 0.8, 1.2)'
                #},
                {
                    'name':  'lep1_Iso_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "({0}.isEl) ? electron_relativeIsoR03_withEA[{1}] : muon_relativeIsoR04_deltaBeta[{1}]".format(self.lep1_str, self.lep1_fwkIdx),
                    'plot_cut': self.totalCut,
                    'binning': '(50, 0, 0.4)'
                },
                {
                    'name':  'lep2_pt_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': self.lep2_str+".p4.Pt()",
                    'plot_cut': self.totalCut,
                    'binning': '(50, 0, 100)'
                },
                {
                    'name':  'lep2_eta_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': self.lep2_str+".p4.Eta()",
                    'plot_cut': self.totalCut,
                    'binning': '(25, -2.5, 2.5)'
                },
                {
                    'name':  'lep2_phi_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': self.lep2_str+".p4.Phi()",
                    'plot_cut': self.totalCut,
                    'binning': '(25, -3.1416, 3.1416)'
                },
                #{
                #    'name':  'lep2_scaleFactor_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #    'variable': get_lepton_SF(self.lep2_str, self.lepid2, self.lepiso2, "nominal"),
                #    'plot_cut': self.totalCut,
                #    'binning': '(50, 0.8, 1.2)'
                #},
                {
                    'name':  'lep2_Iso_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "({0}.isEl) ? electron_relativeIsoR03_withEA[{1}] : muon_relativeIsoR04_deltaBeta[{1}]".format(self.lep2_str, self.lep2_fwkIdx),
                    'plot_cut': self.totalCut,
                    'binning': '(50, 0, 0.4)'
                }
            ])
            self.plots_jet.extend([ 
                {
                        'name':  'jet1_pt_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 300)'
                },
                {
                        'name':  'jet1_eta_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".p4.Eta()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -2.5, 2.5)'
                },
                {
                        'name':  'jet1_phi_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".p4.Phi()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -3.1416, 3.1416)'
                },
                {
                        'name':  'jet1_JP_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".JP",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.5)'
                },
                {
                        'name':  'jet1_CSV_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".CSV",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 1)'
                },
                {
                        'name':  'jet2_pt_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 250)'
                },
                {
                        'name':  'jet2_eta_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".p4.Eta()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -2.5, 2.5)'
                },
                {
                        'name':  'jet2_phi_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".p4.Phi()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -3.1416, 3.1416)'
                },
                {
                        'name':  'jet2_JP_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".JP",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.5)'
                },
                {
                        'name':  'jet2_CSV_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet2_str+".CSV",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 1)'
                },
                #{
                #        'name':  'jet1_scaleFactor_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': get_csvv2_sf(self.btagWP1, self.jet1_fwkIdx),
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0.5, 1.5)'
                #},
                #{
                #        'name':  'jet2_scaleFactor_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': get_csvv2_sf(self.btagWP2, self.jet2_fwkIdx),
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0.5, 1.5)'
                #}
            ])

            self.plots_met.extend([ 
                {
                        'name':  'met_pt_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "met_p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 400)'
                },
                {
                        'name':  'met_phi_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "met_p4.Phi()",
                        'plot_cut': self.totalCut,
                        'binning': '(25, -3.1416, 3.1416)'
                }
            ])

            self.plots_ll.extend([ 
                {
                        'name':  'll_M_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.ll_str+".p4.M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 250)'
                },
                {
                        'name':  'll_pt_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.ll_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 400)'
                },
                {
                        'name':  'll_DR_l_l_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.ll_str+".DR_l_l",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'll_DPhi_l_l_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.ll_str+".DPhi_l_l)",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                #{
                #        'name':  'll_scaleFactor_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': get_leptons_SF(self.ll_str, self.lepid1, self.lepid2, self.lepiso1, self.lepiso2, "nominal"),
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0.8, 1.2)'
                #}
            ])

            self.plots_jj.extend([ 
                {
                        'name':  'jj_M_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jj_str+".p4.M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 600)'
                },
                {
                        'name':  'jj_pt_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jj_str+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 400)'
                },
                {
                        'name':  'jj_DR_j_j_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jj_str+".DR_j_j",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'jj_DPhi_j_j_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.jj_str+".DPhi_j_j)",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name':  'jj_CSVprod_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".CSV * " + self.jet2_str+".CSV",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 1)'
                },
                {
                        'name':  'jj_CSVsum_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.jet1_str+".CSV + " + self.jet2_str+".CSV",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 2)'
                },
                #{
                #        'name':  'jj_scaleFactor_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': "{0} * {1}".format(get_csvv2_sf(self.btagWP1, self.jet1_fwkIdx), get_csvv2_sf(self.btagWP2, self.jet2_fwkIdx)),
                #        'plot_cut': self.totalCut,
                #        'binning': '(50, 0.5, 1.5)'
                #} 
            ])

            self.plots_llmetjj.extend([ 
                #{
                #        'name':  'llmetjj_n_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #        'variable': "Length$(%s)"%self.mapIndices,
                #        'plot_cut': self.totalCut,
                #        'binning': '(18, 0, 18)'
                #},
                {
                        'name':  'llmetjj_pt_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 250)'
                },
                {
                        'name':  'llmetjj_M_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".p4.M()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 1000)'
                },
                {
                        'name':  'llmetjj_DPhi_ll_met_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".DPhi_ll_met)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                },
                {
                        'name':  'llmetjj_minDPhi_l_met_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".minDPhi_l_met",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name':  'llmetjj_maxDPhi_l_met_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".maxDPhi_l_met",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name':  'llmetjj_MT_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".MT", # ll[ill].p4 + met[imet].p4).M()
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 600)'
                },
                {
                        'name':  'llmetjj_MTformula_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".MT_formula", # std::sqrt(2 * ll[ill].p4.Pt() * met[imet].p4.Pt() * (1-std::cos(dphi)));
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 500)'
                },
                {
                        'name':  'llmetjj_projMET_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".projectedMet)",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 400)'
                },
                {
                        'name':  'llmetjj_DPhi_jj_met_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".DPhi_jj_met)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                },
                {
                        'name':  'llmetjj_minDPhi_j_met_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".minDPhi_j_met",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name':  'llmetjj_maxDPhi_j_met_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".maxDPhi_j_met",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 3.1416)'
                },
                {
                        'name':  'llmetjj_maxDR_l_j_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".maxDR_l_j",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'llmetjj_minDR_l_j_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".minDR_l_j",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'llmetjj_DR_ll_jj_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".DR_ll_jj",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'llmetjj_DR_llmet_jj_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".DR_llmet_jj",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 6)'
                },
                {
                        'name':  'llmetjj_DPhi_ll_jj_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".DPhi_ll_jj)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                },
                {
                        'name':  'llmetjj_DPhi_llmet_jj_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".DPhi_llmet_jj)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 3.1416)'
                },
                {
                        'name':  'llmetjj_cosThetaStar_CS_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': "abs("+self.baseObject+".cosThetaStar_CS)",
                        'plot_cut': self.totalCut,
                        'binning': '(25, 0, 1)'
                },
                {
                        'name':  'lljj_pt_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".lljj_p4.Pt()",
                        'plot_cut': self.totalCut,
                        'binning': '(50, 0, 500)'
                },
                {
                        'name':  'lljj_M_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                        'variable': self.baseObject+".lljj_p4.M()",
                        'plot_cut': self.totalCut,
                        'binning': '(75, 0, 1000)'
                }
            ])
            # gen level plots for jj 
            for elt in self.plots_jj : 
                tempPlot = copy.deepcopy(elt)
                if "p4" in tempPlot["variable"] :
                    tempPlot["variable"] = tempPlot["variable"].replace(self.jj_str,"hh_gen_BB")
                    tempPlot["name"] = "gen"+tempPlot["name"]
                    self.plots_gen.append(tempPlot)
#            self.plots_evt.extend([ # broken if we do not use maps
#                {
#                    'name':  'nLep_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
#                    'variable': "Length$(%s)"%self.lepMapIndices,
#                    'plot_cut': self.totalCut,
#                    'binning': '(4, 2, 6)'
#                },
#                {
#                    'name':  'nLepAll_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.jjIDCat, self.jjBtagCat, self.suffix),
#                    'variable': "hh_nLeptons",
#                    'plot_cut': self.totalCut,
#                    'binning': '(5, 2, 7)'
#                },
#                {
#                    'name':  'nElAll_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.jjIDCat, self.jjBtagCat, self.suffix),
#                    'variable': "hh_nElectrons",
#                    'plot_cut': self.totalCut,
#                    'binning': '(6, 0, 6)'
#                },
#                {
#                    'name':  'nMuAll_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.jjIDCat, self.jjBtagCat, self.suffix),
#                    'variable': "hh_nMuons",
#                    'plot_cut': self.totalCut,
#                    'binning': '(6, 0, 6)'
#                },
#                {
#                    'name':  'nJet_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
#                    'variable': "Length$(%s)"%self.jetMapIndices,
#                    'plot_cut': self.totalCut,
#                    'binning': '(5, 2, 7)'
#                },
#                {
#                    'name':  'nJetAll_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.jjIDCat, self.jjBtagCat, self.suffix),
#                    'variable': "hh_nJets",
#                    'plot_cut': self.totalCut,
#                    'binning': '(10, 2, 12)'
#                },
#                {
#                    'name':  'nBJetLooseCSV_%s_jetID_%s_btag_%s%s'%(self.llFlav, self.jjIDCat, self.jjBtagCat, self.suffix),
#                    'variable': "hh_nBJetsL",
#                    'plot_cut': self.totalCut,
#                    'binning': '(6, 0, 6)'
#                }
#            ])
            self.forSkimmer.extend([
                {
                    'name':  'event_weight_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "event_weight",
                    'plot_cut': self.totalCut,
                    'binning': '(500, -10000, 10000)'
                },
                #{
                #    'name':  'total_weight_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                #    'variable': "event_weight * event_pu_weight * {0} * {1} * ".format(get_csvv2_sf(self.btagWP1, self.jet1_fwkIdx), get_csvv2_sf(self.btagWP2, self.jet2_fwkIdx)) + get_leptons_SF(self.ll_str, self.lepid1, self.lepid2, self.lepiso1, self.lepiso2, "nominal"),
                #    'plot_cut': self.totalCut,
                #    'binning': '(5, -2, 2)'
                #},
                {
                    'name':  'event_pu_weight_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "event_pu_weight",
                    'plot_cut': self.totalCut,
                    'binning': '(50, 0, 6)'
                },
                {
                    'name':  'isElEl_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "%s.isElEl"%self.ll_str,
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name':  'isMuMu_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "%s.isMuMu"%self.ll_str,
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name':  'isElMu_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "%s.isElMu"%self.ll_str,
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name':  'isMuEl_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "%s.isMuEl"%self.ll_str,
                    'plot_cut': self.totalCut,
                    'binning': '(2, 0, 2)'
                },
                {
                    'name':  'event_number_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "event_event",
                    'plot_cut': self.totalCut,
                    'binning': '(300, 0, 300000)'
                },
                {
                    'name':  'event_run_%s_%s%s%s'%(self.llFlav, self.suffix, self.extraString, self.systematicString),
                    'variable': "event_run",
                    'plot_cut': self.totalCut,
                    'binning': '(300, 0, 300000)'
                }
            ])

            # MVA evaluation : ugly but necessary part
            baseStringForMVA_part1 = 'evaluateMVA("/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/HHTools/mvaTraining_hh/weights/BDTNAME_kBDT.weights.xml", '
            baseStringForMVA_part2 = '{{"jj_pt", %s}, {"ll_pt", %s}, {"ll_M", %s}, {"ll_DR_l_l", %s}, {"jj_DR_j_j", %s}, {"llmetjj_DPhi_ll_jj", %s}, {"llmetjj_minDR_l_j", %s}, {"llmetjj_MTformula", %s}})'%(self.jj_str+".p4.Pt()", self.ll_str+".p4.Pt()", self.ll_str+".p4.M()", self.ll_str+".DR_l_l", self.jj_str+".DR_j_j", self.baseObject+".minDR_l_j", self.baseObject+".DPhi_ll_jj", self.baseObject+".MT_formula")

            stringForMVA = baseStringForMVA_part1 + baseStringForMVA_part2

            # The following will need to be modified each time the name of the BDT output changes
            bdtNameTemplate = "DATE_BDT_XSPIN_MASS_SUFFIX"
            date = "2016_01_17"
            spins = ["0"] #, "2"]
            masses = ["400", "650", "900"]
            suffixs = ["VS_TT09_DY01_8var_bTagMM"] #, "VS_TT1_DY0_8var_bTagMM"]

            for spin in spins :
                for mass in masses :
                    for suffix in suffixs :
                        bdtName = bdtNameTemplate.replace("DATE", date).replace("SPIN", spin).replace("MASS", mass).replace("SUFFIX", suffix)
                        stringForMVA = baseStringForMVA_part1.replace("BDTNAME", bdtName) + baseStringForMVA_part2
                        self.plots_mva.append({
                            "name" : "MVA_%s_%s_%s%s"%(bdtName, self.llFlav, self.suffix, self.systematicString),
                            "variable" : stringForMVA,
                            "plot_cut" : self.totalCut,
                            "binning" : "(50, -0.6, 0.6)"
                        })
                        self.crucial_plots.append({
                            "name" : "MVA_%s_%s_%s%s"%(bdtName, self.llFlav, self.suffix, self.systematicString),
                            "variable" : stringForMVA,
                            "plot_cut" : self.totalCut,
                            "binning" : "(50, -0.6, 0.6)"
                        })
            for weight in weightsToPlot.keys() : 
                self.plots_weights.append({'name':  '%s_%s_%s%s'%(weight, self.llFlav, self.suffix, self.systematicString), 'variable': weightsToPlot[weight], 'plot_cut': self.totalCut, 'binning': '(50, 0, 2)', 'weight': 'event_weight'})

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

