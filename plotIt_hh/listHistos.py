#usage : python listHisto.py (optional) suffix for yml file
from ROOT import * 
import sys  
baseDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/" 
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
fileName = baseDir+"CommonTools/histFactory/hists_TTsystematics/condor/output/TTTo2L2Nu_13TeV-powheg_MiniAODv2_v2.0.3+7415_HHAnalysis_2016-01-30.v2_histos.root"

skim = False

file = TFile(fileName) 
keys = file.GetListOfKeys() 
f = open("allPlots.yml", 'w')
#if skim :
#    f = open("allPlots.yml", 'w')
#elif len(sys.argv) == 2 :
#    fmumu = open("mumuPlots"+"_"+sys.argv[1]+".yml",'w') 
#    felel = open("elelPlots"+"_"+sys.argv[1]+".yml",'w') 
#    fmuel = open("muelPlots"+"_"+sys.argv[1]+".yml",'w') 
#else: 
#    fmumu = open("mumuPlots.yml",'w') 
#    felel = open("elelPlots.yml",'w') 
#    fmuel = open("muelPlots.yml",'w') 

alreadyIn = []

commonString_yEvtPerGeV = '  y-axis: "Events"\n  y-axis-format: "%1% / %2$.0f GeV"\n  normalized: false\n  log-y: both\n  save-extensions: ["png","pdf"]\n  legend-columns: 2\n  show-ratio: true\n  show-overflow: true\n  show-errors: true\n  for-yields: true\n'
commonString_yEvt = commonString_yEvtPerGeV.replace(" / %2$.0f GeV"," / %2$.0f")
#commonString_yEvt = '  y-axis: "#Event"\n  y-axis-format: "%1%" \n  normalized: false\n  log-y: both\n  save-extensions: ["png","pdf"]\n  show-ratio: true\n  show-overflow: true\n\n'
for key in keys :
    if key.GetName() not in alreadyIn  and not "__" in key.GetName() :
        alreadyIn.append(key.GetName())
        x_axis = '  x-axis: "'+key.GetName()+'"\n'
        finalString = x_axis + commonString_yEvt

        if "lep1_pt" in key.GetName() :
            x_axis = x_axis.replace(key.GetName(), "p_{T}^{l1} (GeV)")
            finalString = x_axis + commonString_yEvtPerGeV
        elif "lep2_pt" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "p_{T}^{l2} (GeV)")
            finalString = x_axis + commonString_yEvtPerGeV
        elif "jet1_pt" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "p_{T}^{j1} (GeV)")
            finalString = x_axis + commonString_yEvtPerGeV
        elif "jet2_pt" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "p_{T}^{j2} (GeV)")
            finalString = x_axis + commonString_yEvtPerGeV
        elif "lep1_eta" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#eta_{l1}")
            finalString = x_axis + commonString_yEvt
        elif "lep2_eta" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#eta_{l2}")
            finalString = x_axis + commonString_yEvt
        elif "jet1_eta" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#eta_{j1}")
            finalString = x_axis + commonString_yEvt
        elif "jet2_eta" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#eta_{j2}")
            finalString = x_axis + commonString_yEvt
        elif "lep1_phi" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#phi_{l1}")
            finalString = x_axis + commonString_yEvt
        elif "lep2_phi" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#phi_{l2}")
            finalString = x_axis + commonString_yEvt
        elif "jet1_phi" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#phi_{j1}")
            finalString = x_axis + commonString_yEvt
        elif "jet2_phi" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#phi_{j2}")
            finalString = x_axis + commonString_yEvt
        elif "jet1_CSV" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "CSV_{j1}")
            finalString = x_axis + commonString_yEvt
        elif "jet2_CSV" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "CSV_{j2}")
            finalString = x_axis + commonString_yEvt
        elif "jet1_JP" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "JP_{j1}")
            finalString = x_axis + commonString_yEvt
        elif "jet2_JP" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "JP_{j2}")
            finalString = x_axis + commonString_yEvt
        elif "ll_M_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "m_{ll} (GeV)")
            finalString = x_axis + commonString_yEvtPerGeV
        elif "jj_M_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "m_{jj} (GeV)")
            finalString = x_axis + commonString_yEvtPerGeV
        elif "ll_pt_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "p_{T}^{ll} (GeV)")
            finalString = x_axis + commonString_yEvtPerGeV
        elif "jj_pt_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "p_{T}^{jj} (GeV)")
            finalString = x_axis + commonString_yEvtPerGeV
        elif "met_pt" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#slash{E}_{T} (GeV)")
            finalString = x_axis + commonString_yEvtPerGeV
        elif "met_phi" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#phi_{#slash{E}_{T}}")
            finalString = x_axis + commonString_yEvt
        elif "ll_DR_l_l" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#DeltaR(l1, l2)")
            finalString = x_axis + commonString_yEvt
        elif "jj_DR_j_j" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#DeltaR(j1, j2)")
            finalString = x_axis + commonString_yEvt
        elif "ll_DPhi_l_l" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#Delta#phi(l1, l2)")
            finalString = x_axis + commonString_yEvt
        elif "jj_DPhi_j_j" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#Delta#phi(j1, j2)")
            finalString = x_axis + commonString_yEvt
        elif "llmetjj_pt_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "p_{T}^{lljj#slash{E}_{T}}")
            finalString = x_axis + commonString_yEvtPerGeV
        elif "llmetjj_M_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "m_{lljj#slash{E}_{T}}")
            finalString = x_axis + commonString_yEvtPerGeV
        elif "DPhi_ll_met_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#Delta#phi(ll, #slash{E}_{T})")
            finalString = x_axis + commonString_yEvt
        elif "DPhi_ll_jj" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#Delta#phi(ll, jj)")
            finalString = x_axis + commonString_yEvt
        elif "minDPhi_l_met_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "min(#Delta#phi(l, #slash{E}_{T}))")
            finalString = x_axis + commonString_yEvt
        elif "maxDPhi_l_met_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "max(#Delta#phi(l, #slash{E}_{T}))")
            finalString = x_axis + commonString_yEvt
        elif "MT_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "m_{ll#slash{E}_{T}}")
            finalString = x_axis + commonString_yEvtPerGeV
        elif "MTformula_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "MT")
            finalString = x_axis + commonString_yEvtPerGeV
        elif "projMET_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "Projected #slash{E}_{T}")
            finalString = x_axis + commonString_yEvtPerGeV
        elif "DPhi_jj_met" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#Delta#phi(jj, #slash{E}_{T})")
            finalString = x_axis + commonString_yEvt
        elif "minDPhi_j_met" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "min#Delta#phi(j, #slash{E}_{T})")
            finalString = x_axis + commonString_yEvt
        elif "maxDPhi_j_met" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "max#Delta#phi(j, #slash{E}_{T})")
            finalString = x_axis + commonString_yEvt
        elif "minDR_l_j" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "min#DeltaR(l, j)")
            finalString = x_axis + commonString_yEvt
        elif "maxDR_l_j" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "max#DeltaR(l, j)")
            finalString = x_axis + commonString_yEvt
        elif "DR_ll_jj_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#DeltaR(ll, jj)")
            finalString = x_axis + commonString_yEvt
        elif "DR_llmet_jj" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#DeltaR(ll#slash{E}_{T}, jj)")
            finalString = x_axis + commonString_yEvt
        elif "DPhi_ll_jj_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#DeltaPhi(ll, jj)")
            finalString = x_axis + commonString_yEvt
        elif "nllmetjj_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#llmetjj")
            finalString = x_axis + commonString_yEvt
        elif "nLep_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#leptons")
            finalString = x_axis + commonString_yEvt
        elif "nJet_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "#jets")
            finalString = x_axis + commonString_yEvt
        elif "nBJetMediumCSV_" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "# B jets (CSV M)")
            finalString = x_axis + commonString_yEvt
        elif "cosThetaStar_CS" in key.GetName() :  
            x_axis = x_axis.replace(key.GetName(), "cos(#theta^{*}_{CS})")
            finalString = x_axis + commonString_yEvt
        elif "BDT" in key.GetName() :
            x_axis = x_axis.replace(key.GetName(), "BDT output")
            finalString = x_axis + commonString_yEvt + '  blinded-range: [-0.19, 0.6]\n' #  blinded-range-fill-color: "#29556270"\n  blinded-range-fill-style: 1001\n'
        elif "scaleFactor" in key.GetName() :
            x_axis = x_axis.replace(key.GetName(), "Scale Factor")
            finalString = x_axis + commonString_yEvt + '  no-data: true\n'

        if "MuMu" in key.GetName() : 
            f.write("'"+key.GetName()+"'"+":\n") 
            f.write(finalString)
            f.write('  extra-label: "Preliminary - DiMuon Channel"\n\n')
            #break
        elif "ElEl" in key.GetName() : 
            f.write("'"+key.GetName()+"'"+":\n") 
            f.write(finalString)
            f.write('  extra-label: "Preliminary - DiElectron Channel"\n\n')
        elif "MuEl" in key.GetName() : 
            f.write("'"+key.GetName()+"'"+":\n") 
            f.write(finalString)
            f.write('  extra-label: "Preliminary - MuEl Channel"\n\n')
        elif "All" in key.GetName() : 
            f.write("'"+key.GetName()+"'"+":\n") 
            f.write(finalString)
            f.write('  extra-label: "Preliminary - All Channels"\n\n')
        
#        if skim :
#            f.write("'"+key.GetName()+"'"+":\n") 
#            f.write(finalString)
#            print key.GetName()
#            f.write('  extra-label: "Preliminary - All Channels"\n\n')
#            continue
#
        #if "MuMu" in key.GetName() : 
        #    fmumu.write("'"+key.GetName()+"'"+":\n") 
        #    fmumu.write(finalString)
        #    fmumu.write('  extra-label: "Preliminary - DiMuon Channel"\n\n')
        #    #break
        #elif "ElEl" in key.GetName() : 
        #    felel.write("'"+key.GetName()+"'"+":\n") 
        #    felel.write(finalString)
        #    felel.write('  extra-label: "Preliminary - DiElectron Channel"\n\n')
        #elif "MuEl" in key.GetName() : 
        #    fmuel.write("'"+key.GetName()+"'"+":\n") 
        #    fmuel.write(finalString)
        #    fmuel.write('  extra-label: "Preliminary - MuEl Channel"\n\n')
        #elif "All" in key.GetName() : 
        #    fmuel.write("'"+key.GetName()+"'"+":\n") 
        #    fmuel.write(finalString)
        #    fmuel.write('  extra-label: "Preliminary - All Channels"\n\n')


        #f.write("'"+key.GetName()+"'"+":\n") 
        #f.write('  x-axis: "'+key.GetName()+'"\n  y-axis: "Evt"\n  y-axis-format: "%1% / %2$.0f GeV"\n  normalized: false\n  x-axis-range: [0, 250]\n  log-y: true\n  save-extensions: ["png"]\n  show-ratio: true\n')



