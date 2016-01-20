import sys
sys.path.append("../../CommonTools/mvaTraining/")
from tmvaTools import * 

date = "2016_01_17"
suffix = "test" #"VS_TT09_DY01_8var_bTagMM"
label_template = "DATE_BDT_XSPIN_MASS_SUFFIX"

massPoints = ['400', '650', '900']
spins = ["0", "2"]
inFileDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/CommonTools/treeFactory/allFlavour_trigger_btagMM_2016_01_14/condor/output/"
bkgFiles = { 
        "TT" : { 
                    "files" : [inFileDir+"TTTo2L2Nu_13TeV-powheg_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"],
                    "relativeWeight" : 0.90
                },
        "DY" : { 
                    "files" : [inFileDir+"DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root", inFileDir+"DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"],
                    "relativeWeight" : 0.10
                }
        }
discriList = [
        "jj_pt",
        "ll_pt",
        "ll_M",
        "ll_DR_l_l",
        "jj_DR_j_j",
        "llmetjj_DPhi_ll_jj",
        "llmetjj_minDR_l_j",
        #"llmetjj_projMET",
        "llmetjj_MTformula"
        ]
cut = "(91.1876 - ll_M) > 15 && ll_DR_l_l < 2.2 && jj_DR_j_j < 3.1 && llmetjj_DPhi_ll_jj > 1.5"
MVAmethods = ["kBDT"]
weightExpr = "event_weight*ll_scaleFactor*jj_scaleFactor"

spectatorList = ['lep1_pt', 'lep1_eta', 'lep1_phi', 'lep1_Iso', 'lep2_pt', 'lep2_eta', 'lep2_phi', 'lep2_Iso', 'jet1_pt', 'jet1_eta', 'jet1_phi', 'jet1_JP', 'jet1_CSV', 'jet2_pt', 'jet2_eta', 'jet2_phi', 'jet2_JP', 'jet2_CSV', 'met_pt', 'met_phi', 'll_DPhi_l_l', 'jj_M', 'jj_DPhi_j_j', 'llmetjj_n', 'llmetjj_pt', 'llmetjj_M', 'llmetjj_DPhi_ll_met', 'llmetjj_minDPhi_l_met', 'llmetjj_maxDPhi_l_met', 'llmetjj_MT', 'llmetjj_DPhi_jj_met', 'llmetjj_minDPhi_j_met', 'llmetjj_maxDPhi_j_met', 'llmetjj_maxDR_l_j', 'llmetjj_DR_ll_jj', 'llmetjj_DR_llmet_jj', 'llmetjj_DPhi_llmet_jj', 'llmetjj_cosThetaStar_CS', 'lljj_pt', 'lljj_M', 'nLep', 'nLepAll', 'nElAll', 'nMuAll', 'nJet', 'nJetAll', 'nBJetLooseCSV', 'event_weight', 'isElEl', 'isMuMu', 'isElMu', 'isMuEl']

if __name__ == '__main__':
    for mass in massPoints :
        for spin in spins :
            if spin == "0" :
                sigFiles = {
                            "X%s_%s"%(spin, mass) : 
                            {
                                "files" : [inFileDir+"GluGluToRadionToHHTo2B2VTo2L2Nu_M-%s_narrow_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"%mass],
                                "relativeWeight" : 1.
                            }
                        }
            elif spin == "2" : 
                sigFiles = {
                            "X%s_%s"%(spin, mass) : 
                            {
                                "files" : [inFileDir+"GluGluToBulkGravitonToHHTo2B2VTo2L2Nu_M-%s_narrow_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"%mass],
                                "relativeWeight" : 1.
                            }
                        }
            else : 
                print "Spin choice has to be '0' or '2'."
            label = label_template.replace("DATE", date).replace("SPIN", spin).replace("MASS", mass).replace("SUFFIX", suffix)
            label = "2016_01_17_BDT_X%s_%s_VS_TT09_DY01_8var_bTagMM"%(spin, mass)
            print bkgFiles, sigFiles
            trainMVA(bkgFiles, sigFiles, discriList, cut, weightExpr, MVAmethods, spectatorList, label)




