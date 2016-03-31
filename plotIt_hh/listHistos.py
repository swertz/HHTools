#! /usr/bin/env python

import yaml

#usage : python listHisto.py [yields]
from ROOT import * 
import argparse

parser = argparse.ArgumentParser(description='Facility to produce the yml with plots information.')
parser.add_argument('--yields', help='If you just want to produce the yields and systematics.', action="store_true")
parser.add_argument('-m', '--mass', dest='mass', default="650", help='Mass point for the yields.')
parser.add_argument('-d', '--directory', dest='directory', default="histos_for_PUBPAS", help='Directory of the input rootfiles.')
args = parser.parse_args()

baseDir = "/nfs/user/llbb/HIG16011/" 
#fileName = baseDir+"avoidTFormula/CommonTools/histFactory/hists_TTTT_jetidT_htOrdered/GluGluToRadionToHHTo2B2VTo2L2Nu_M-500_narrow_MiniAODv2_v1.0.0+7415_HHAnalysis_2015-10-20.v4_histos.root"
#fileName = baseDir+"CommonTools/histFactory/hists_MllLower80/GluGluToRadionToHHTo2B2VTo2L2Nu_M-500_narrow_MiniAODv2_v1.0.0+7415_HHAnalysis_2015-10-20.v4_histos.root"
#fileName = baseDir+"CommonTools/histFactory/hists_LLLL_jetidL_csvANDhtOrdered/condor/output/VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8_MiniAODv2_v1.0.0+7415_HHAnalysis_2015-10-20.v4_histos.root"
#fileName = baseDir+"CommonTools/histFactory/histMllmetAbove650/condor/output/VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8_MiniAODv2_v1.0.0+7415_HHAnalysis_2015-10-20.v4_histos.root"
#fileName = baseDir+"CommonTools/histFactory/hists_TTTT_jetidL_csvOrdered/condor/output/VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8_MiniAODv2_v1.0.0+7415_HHAnalysis_2015-10-20.v4_histos.root"
#fileName = baseDir+"CommonTools/histFactory/MllZ_MjjZ/condor/output/VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"
#fileName = baseDir+"CommonTools/histFactory/hists_withMVA650/TT_TuneCUETP8M1_13TeV-powheg-pythia8_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"
#fileName = baseDir+"CommonTools/histFactory/hists_withAllMVA/GluGluToRadionToHHTo2B2VTo2L2Nu_M-900_narrow_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"
#fileName = baseDir+"CommonTools/histFactory/hists_skimmed_btagLL_nocut_2016_01_14/GluGluToRadionToHHTo2B2VTo2L2Nu_M-900_narrow_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"
#fileName = baseDir+"CommonTools/histFactory/hists_TTTT_jetidL_csvOrdered_2016_01_14/condor/output/GluGluToRadionToHHTo2B2VTo2L2Nu_M-900_narrow_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"
#fileName = baseDir+"CommonTools/histFactory/hists_skimmed_btagLL_plentyMVA_2016_01_14/GluGluToRadionToHHTo2B2VTo2L2Nu_M-900_narrow_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"
#fileName = baseDir+"CommonTools/histFactory/hists_skimmed_btagMM_bdtCut_2016_01_17/GluGluToRadionToHHTo2B2VTo2L2Nu_M-900_narrow_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"
#fileName = baseDir+"CommonTools/histFactory/hists_TTTT_jetidL_csvOrdered_2016_01_14_noOverlapRemoval/condor/output/GluGluToRadionToHHTo2B2VTo2L2Nu_M-900_narrow_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"

#fileName = baseDir+"CommonTools/histFactory/hists_TTTT_jetidL_csvOrdered_2016_01_15_puweight/condor/output/TTTo2L2Nu_13TeV-powheg_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"
#fileName = baseDir+"CommonTools/histFactory/2016-02-04-fullPlots/condor/output/TTTo2L2Nu_13TeV-powheg_MiniAODv2_v2.0.3+7415_HHAnalysis_2016-01-30.v2_histos.root"
#fileName = baseDir+"CommonTools/histFactory/raisePtCut/condor/output/GluGluToRadionToHHTo2B2VTo2L2Nu_M-900_narrow_MiniAODv2_v2.0.3+7415_HHAnalysis_2016-01-30.v2_histos.root"
#fileName = baseDir+"CommonTools/histFactory/newBDT_TTonly_properControl/condor/output/GluGluToRadionToHHTo2B2VTo2L2Nu_M-900_narrow_MiniAODv2_v2.0.3+7415_HHAnalysis_2016-01-30.v3_histos.root"
#fileName = baseDir+"/HHTools/histFactory_hh/controlRegions/condor/output/GluGluToRadionToHHTo2B2VTo2L2Nu_M-900_narrow_MiniAODv2_v2.0.3+7415_HHAnalysis_2016-01-30.v3_histos.root"
#fileName = baseDir+"/HHTools/histFactory_hh/signalRegion/condor/output/GluGluToRadionToHHTo2B2VTo2L2Nu_M-900_narrow_MiniAODv2_v2.0.3+7415_HHAnalysis_2016-01-30.v3_histos.root"
#fileName = baseDir+"/HHTools/histFactory_hh/2016-02-18_newBDT_HT_genericPlots/condor/output/GluGluToRadionToHHTo2B2VTo2L2Nu_M-900_narrow_MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0_histos.root"
#fileName = baseDir+"/HHTools/histFactory_hh/forYieldsBis/condor/output/GluGluToRadionToHHTo2B2VTo2L2Nu_M-900_narrow_MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0_histos.root"
fileName = baseDir+args.directory+"/GluGluToRadionToHHTo2B2VTo2L2Nu_M-900_narrow_MiniAODv2_v2.0.5+7415_HHAnalysis_2016-02-24.v0_histos.root"

skim = False

file = TFile(fileName) 
keys = file.GetListOfKeys() 
alreadyIn = []

# Dictionary containing all the plots
plots = {}

logY = 'both'
if args.yields :
    logY = False
defaultStyle = {
        'log-y': logY,
        'save-extensions': ['pdf', 'png'],
        'legend-columns': 2,
        'show-ratio': True,
        'show-overflow': True,
        'show-errors': True
        }

defaultStyle_events_per_gev = defaultStyle.copy()
defaultStyle_events_per_gev.update({
        'y-axis': 'Events',
        'y-axis-format': '%1% / %2$.2f GeV',
        })

defaultStyle_events = defaultStyle.copy()
defaultStyle_events.update({
        'y-axis': 'Events',
        'y-axis-format': '%1% / %2$.2f',
        })

for key in keys :
    if key.GetName() not in alreadyIn  and not "__" in key.GetName():
        alreadyIn.append(key.GetName())
        plot = {
                'x-axis': key.GetName(),
                }

        if "lep1_pt" in key.GetName() :
            plot['x-axis'] = "Leading lepton p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "lep2_pt" in key.GetName() :  
            plot['x-axis'] = "Sub-leading lepton p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "jet1_pt" in key.GetName() :  
            plot['x-axis'] = "Leading jet p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "jet2_pt" in key.GetName() :  
            plot['x-axis'] = "Sub-leading jet p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "lep1_eta" in key.GetName() :  
            plot['x-axis'] = "Leading jet #eta"
            plot.update(defaultStyle_events)
        elif "lep2_eta" in key.GetName() :  
            plot['x-axis'] = "Sub-leading jet #eta"
            plot.update(defaultStyle_events)
        elif "jet1_eta" in key.GetName() :  
            plot['x-axis'] = "Leading jet #eta"
            plot.update(defaultStyle_events)
        elif "jet2_eta" in key.GetName() :  
            plot['x-axis'] = "Sub-leading jet #eta"
            plot.update(defaultStyle_events)
        elif "lep1_phi" in key.GetName() :  
            plot['x-axis'] = "Leading lepton #phi"
            plot.update(defaultStyle_events)
        elif "lep2_phi" in key.GetName() :  
            plot['x-axis'] = "Sub-leading lepton #phi"
            plot.update(defaultStyle_events)
        elif "jet1_phi" in key.GetName() :  
            plot['x-axis'] = "Leading jet #phi"
            plot.update(defaultStyle_events)
        elif "jet2_phi" in key.GetName() :  
            plot['x-axis'] = "Sub-leading jet #phi"
            plot.update(defaultStyle_events)
        elif "jet1_CSV" in key.GetName() :  
            plot['x-axis'] = "Leading jet CSVv2 discriminant"
            plot.update(defaultStyle_events)
        elif "jet2_CSV" in key.GetName() :  
            plot['x-axis'] = "Sub-leading jet CSVv2 discriminant"
            plot.update(defaultStyle_events)
        elif "jet1_JP" in key.GetName() :  
            plot['x-axis'] = "Leading jet JP discriminant"
            plot.update(defaultStyle_events)
        elif "jet2_JP" in key.GetName() :  
            plot['x-axis'] = "Sub-leading jet JP discriminant"
            plot.update(defaultStyle_events)
        elif "ll_M_" in key.GetName() :  
            plot['x-axis'] = "m_{ll} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "ll_pt_" in key.GetName() :  
            plot['x-axis'] = "Dilepton system p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "jj_pt_" in key.GetName() :  
            plot['x-axis'] = "Dijet system p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "met_pt" in key.GetName() :  
            plot['x-axis'] = "#slash{E}_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "met_phi" in key.GetName() :  
            plot['x-axis'] = "#phi_{#slash{E}_{T}}"
            plot.update(defaultStyle_events)
        elif "ll_DR_l_l_All_hh_llmetjj_HWWleptons_btagM_csv_cleaning_cut" in key.GetName() :  
            plot['x-axis'] = "#DeltaR(leading lepton, sub-leading lepton)"
            plot.update(defaultStyle_events)
        elif "ll_DR_l_l" in key.GetName() :  
            plot['x-axis'] = "#DeltaR(leading lepton, sub-leading lepton)"
            plot.update(defaultStyle_events)
        elif "jj_DR_j_j" in key.GetName() :  
            plot['x-axis'] = "#DeltaR(leading jet, sub-leading jet)"
            plot.update(defaultStyle_events)
        elif "ll_DPhi_l_l" in key.GetName() :  
            plot['x-axis'] = "#Delta#phi(leading lepton, sub-leading lepton)"
            plot.update(defaultStyle_events)
        elif "jj_DPhi_j_j" in key.GetName() :  
            plot['x-axis'] = "#Delta#phi(leading jet, sub-leading jet)"
            plot.update(defaultStyle_events)
        elif "llmetjj_pt_" in key.GetName() :  
            plot['x-axis'] = "p_{T}^{lljj#slash{E}_{T}}"
            plot.update(defaultStyle_events_per_gev)
        elif "llmetjj_M_" in key.GetName() :  
            plot['x-axis'] = "m_{lljj#slash{E}_{T}}"
            plot.update(defaultStyle_events_per_gev)
        elif "DPhi_ll_met_" in key.GetName() :  
            plot['x-axis'] = "#Delta#phi(ll, #slash{E}_{T})"
            plot.update(defaultStyle_events)
        elif "DPhi_ll_jj" in key.GetName() :  
            plot['x-axis'] = "#Delta#phi(ll, jj)"
            plot.update(defaultStyle_events)
        elif "minDPhi_l_met_" in key.GetName() :  
            plot['x-axis'] = "min(#Delta#phi(lepton, #slash{E}_{T}))"
            plot.update(defaultStyle_events)
        elif "maxDPhi_l_met_" in key.GetName() :  
            plot['x-axis'] = "max(#Delta#phi(lepton, #slash{E}_{T}))"
            plot.update(defaultStyle_events)
        elif "MT_" in key.GetName() :  
            plot['x-axis'] = "m_{ll#slash{E}_{T}}"
            plot.update(defaultStyle_events_per_gev)
        elif "MTformula_" in key.GetName() :  
            plot['x-axis'] = "MT"
            plot.update(defaultStyle_events_per_gev)
        elif "projMET_" in key.GetName() :  
            plot['x-axis'] = "Projected #slash{E}_{T}"
            plot.update(defaultStyle_events_per_gev)
        elif "DPhi_jj_met" in key.GetName() :  
            plot['x-axis'] = "#Delta#phi(jj, #slash{E}_{T})"
            plot.update(defaultStyle_events)
        elif "minDPhi_j_met" in key.GetName() :  
            plot['x-axis'] = "min#Delta#phi(j, #slash{E}_{T})"
            plot.update(defaultStyle_events)
        elif "maxDPhi_j_met" in key.GetName() :  
            plot['x-axis'] = "max#Delta#phi(j, #slash{E}_{T})"
            plot.update(defaultStyle_events)
        elif "minDR_l_j" in key.GetName() :  
            plot['x-axis'] = "min#DeltaR(l, j)"
            plot.update(defaultStyle_events)
        elif "maxDR_l_j" in key.GetName() :  
            plot['x-axis'] = "max#DeltaR(l, j)"
            plot.update(defaultStyle_events)
        elif "DR_ll_jj_" in key.GetName() :  
            plot['x-axis'] = "#DeltaR(ll, jj)"
            plot.update(defaultStyle_events)
        elif "DR_llmet_jj" in key.GetName() :  
            plot['x-axis'] = "#DeltaR(ll#slash{E}_{T}, jj)"
            plot.update(defaultStyle_events)
        elif "DPhi_ll_jj_" in key.GetName() :  
            plot['x-axis'] = "#DeltaPhi(ll, jj)"
            plot.update(defaultStyle_events)
        elif "nllmetjj_" in key.GetName() :  
            plot['x-axis'] = "#llmetjj"
            plot.update(defaultStyle_events)
        elif "nLep_" in key.GetName() :  
            plot['x-axis'] = "Number of leptons"
            plot.update(defaultStyle_events)
        elif "nJet_" in key.GetName() :  
            plot['x-axis'] = "Number of jets"
            plot.update(defaultStyle_events)
        elif "nBJetMediumCSV_" in key.GetName() :  
            plot['x-axis'] = "Number of b-tagged jets (CSVv2 medium)"
            plot.update(defaultStyle_events)
        elif "cosThetaStar_CS" in key.GetName() :  
            plot['x-axis'] = "cos(#theta^{*}_{CS})"
            plot.update(defaultStyle_events)
        elif "MVA" in key.GetName() and "mjj_cr" in key.GetName() :
            plot['x-axis'] = "BDT output"
            plot.update(defaultStyle_events)
            #plot['blinded-range'] = [0, 0.6]
        elif "jj_M_" in key.GetName() and "_cr_" in key.GetName() :  
            plot['x-axis'] = "m_{jj} (GeV)"
            plot.update(defaultStyle_events_per_gev)
            #plot['blinded-range'] = [75, 140]
        elif "MVA_" in key.GetName() :
            plot['x-axis'] = "BDT output"
            plot.update(defaultStyle_events)
            plot['blinded-range'] = [0, 0.6]
            #plot['for-yields'] = True
        elif "jj_M_" in key.GetName() :  
            plot['x-axis'] = "m_{jj} (GeV)"
            plot.update(defaultStyle_events_per_gev)
            plot['blinded-range'] = [75, 140]
        elif "isElEl" in key.GetName() and "highBDT_mjjP_" + args.mass in key.GetName() :
            plot['x-axis'] = "isElEl"
            plot.update(defaultStyle_events)
            plot['for-yields'] = True
            plot['yields-title'] = "high-BDT %s, m$_{jj}$-P"%(args.mass)
            plot['yields-table-order'] = 0
        elif "isElEl" in key.GetName() and "highBDT_mjjSB_" + args.mass in key.GetName() :
            plot['x-axis'] = "isElEl"
            plot.update(defaultStyle_events)
            plot['for-yields'] = True
            plot['yields-title'] = "high-BDT %s, m$_{jj}$-SB"%(args.mass)
            plot['yields-table-order'] = 1
        elif "isElEl" in key.GetName() and "lowBDT_mjjP_" + args.mass in key.GetName() :
            plot['x-axis'] = "isElEl"
            plot.update(defaultStyle_events)
            plot['for-yields'] = True
            plot['yields-title'] = "low-BDT %s, m$_{jj}$-P"%(args.mass)
            plot['yields-table-order'] = 2
        elif "isElEl" in key.GetName() and "lowBDT_mjjSB_" + args.mass in key.GetName() :
            plot['x-axis'] = "isElEl"
            plot.update(defaultStyle_events)
            plot['for-yields'] = True
            plot['yields-title'] = "low-BDT %s, m$_{jj}$-SB"%(args.mass)
            plot['yields-table-order'] = 3
        else:
            plot.update(defaultStyle_events)

        if "gen_" in key.GetName():
            flavour = key.GetName().split("_")[1]
            plot['x-axis'] = "is "+flavour
            plot['no-data'] = True
            plot.update(defaultStyle_events)
        if any(x in key.GetName() for x in ['sr_400_ext', 'sr_650_ext']) :
            plot['no-data'] = True
        if "scaleFactor" in key.GetName() :
            plot['x-axis'] = "Scale factor"
            plot.update(defaultStyle_events)
            plot['no-data'] = True

        label_x = 0.22
        label_y = 0.895
        if "MuMu" in key.GetName() : 
            plot['labels'] = [{
                'text': '#mu#mu channel',
                'position': [label_x, label_y],
                'size': 24
                }]
        elif "MuEl" in key.GetName() : 
            plot['labels'] = [{
                'text': '#mue + e#mu channels',
                'position': [label_x, label_y],
                'size': 24
                }]
        elif "All" in key.GetName() : 
            plot['labels'] = [{
                'text': '#mu#mu + ee + #mue + e#mu channels',
                'position': [label_x, label_y],
                'size': 24
                }]
        elif "ElEl" in key.GetName() : #need to be the last one as we use isElEl to compute the yields 
            plot['labels'] = [{
                'text': 'ee channel',
                'position': [label_x, label_y],
                'size': 24
                }]
        if args.yields and "isElEl" in key.GetName() and args.mass in key.GetName() :
            plots[key.GetName()] = plot
        if not args.yields :
            plots[key.GetName()] = plot

with open("allPlots.yml", "w") as f:
    yaml.dump(plots, f)
