import os 


initialDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/plotIt/test/plots/" 

targetDir1 = "plots_noCut_withBtag/"
sourceDir1 = "plots_chan_2016-01-15/"

targetDir2 = "plots_afterMllCut_withBtag/"
sourceDir2 = "plots_all_2016-01-16_mllCut/"

targetDir3 = "plots_afterCleanCut_withBtag/"
sourceDir3 = "plots_all_2016-01-15_bdtCut/"

finalTarget = "brfranco@lxplus.cern.ch:/afs/cern.ch/user/b/brfranco/public/forMiguel_2016_01_21/"

listPlot_noCut_withBtag = [
        sourceDir1.replace("chan","mumu")+"/ll_M_MuMu_lepIso_TT_lepID_TT_jetID_LL_btag_nono_csvOrdered*.pdf",
        sourceDir1.replace("chan","elel")+"/ll_M_ElEl_lepIso_TT_lepID_TT_jetID_LL_btag_nono_csvOrdered*.pdf",
        sourceDir1.replace("chan","muel")+"/ll_M_MuEl_lepIso_TT_lepID_TT_jetID_LL_btag_nono_csvOrdered*.pdf",
        sourceDir1.replace("chan","mumu")+"/ll_M_MuMu_lepIso_TT_lepID_TT_jetID_LL_btag_MM_csvOrdered*.pdf",
        sourceDir1.replace("chan","elel")+"/ll_M_ElEl_lepIso_TT_lepID_TT_jetID_LL_btag_MM_csvOrdered*.pdf",
        sourceDir1.replace("chan","muel")+"/ll_M_MuEl_lepIso_TT_lepID_TT_jetID_LL_btag_MM_csvOrdered*.pdf"
        ]

listPlot_afterMllCut_withBtag = [
        "ll_DR_l_l_lepIso_TT_lepID_TT_jetID_LL_btag_MM_csvOrdered.pdf",
        "jj_DR_j_j_lepIso_TT_lepID_TT_jetID_LL_btag_MM_csvOrdered.pdf",
        "llmetjj_DPhi_ll_jj_lepIso_TT_lepID_TT_jetID_LL_btag_MM_csvOrdered.pdf"
        ]

listPlot_afterCleanCut_withBtag = [
        "ll_M_lepIso_TT_lepID_TT_jetID_LL_btag_MM_csvOrdered.pdf",
        "ll_DR_l_l_lepIso_TT_lepID_TT_jetID_LL_btag_MM_csvOrdered.pdf",
        "jj_DR_j_j_lepIso_TT_lepID_TT_jetID_LL_btag_MM_csvOrdered.pdf",
        "llmetjj_DPhi_ll_jj_lepIso_TT_lepID_TT_jetID_LL_btag_MM_csvOrdered.pdf",
        "ll_pt_lepIso_TT_lepID_TT_jetID_LL_btag_MM_csvOrdered.pdf",
        "jj_pt_lepIso_TT_lepID_TT_jetID_LL_btag_MM_csvOrdered.pdf",
        "jj_M_lepIso_TT_lepID_TT_jetID_LL_btag_MM_csvOrdered.pdf",
        "llmetjj_minDR_l_j_lepIso_TT_lepID_TT_jetID_LL_btag_MM_csvOrdered.pdf",
        "llmetjj_MTformula_lepIso_TT_lepID_TT_jetID_LL_btag_MM_csvOrdered.pdf",
        "MVA_2016_01_15_BDT_X0_*VS_TT1_DY0_8var_bTagMM.pdf"
        ]

if not os.path.isdir(targetDir1) : 
    os.system("mkdir " + targetDir1)
if not os.path.isdir(targetDir2) : 
    os.system("mkdir " + targetDir2)
if not os.path.isdir(targetDir3) : 
    os.system("mkdir " + targetDir3)

for plot in listPlot_noCut_withBtag : 
    command = "cp %s%s %s"%(initialDir, plot, targetDir1)
    os.system(command)

for plot in listPlot_afterMllCut_withBtag : 
    command = "cp %s%s%s %s"%(initialDir, sourceDir2, plot, targetDir2)
    os.system(command)

for plot in listPlot_afterCleanCut_withBtag : 
    command = "cp %s%s%s %s"%(initialDir, sourceDir3, plot, targetDir3)
    os.system(command)

os.system("scp -r %s %s %s %s"%(targetDir1, targetDir2, targetDir3, finalTarget))

sourceDirRocCurve = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/CommonTools/histFactory/hists_skimmed_btagMM_bdtCut_2016_01_17/rocCurve_correct/"
targetDirRocCurve = "rocCurve/"
if not os.path.isdir(targetDirRocCurve) :
    os.system("mkdir " + targetDirRocCurve)

listPlot_rocCurve = [
        "Sample_X*.pdf"
        ]
for plot in listPlot_rocCurve : 
    command = "cp %s%s %s"%(sourceDirRocCurve, plot, targetDirRocCurve)
    os.system(command)

os.system("scp -r %s %s"%(targetDirRocCurve, finalTarget))


