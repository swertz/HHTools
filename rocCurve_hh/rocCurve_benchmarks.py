import os, sys
import ROOT as R
sys.path.append("../../CommonTools/toolBox/")
from rocCurveFacility import *
from drawCanvas import *
R.gROOT.SetBatch()

# Tool to produce ROC curves for all the benchmarks used in the training, and for each BDT
# Usage : python ... outRocPlotDir

inFileDir = "/home/fynu/sbrochet/scratch/Framework/CMSSW_7_6_5/src/cp3_llbb/HHTools/histFactory_hh/160706_all_newjer_newtraining_fixedcluster7_0/condor/output/"

outFileDir = "rocCurve_" + sys.argv[1]
if not os.path.isdir(outFileDir):
    os.system("mkdir " + outFileDir)
print "Will write ROC curves in %s "%(outFileDir)

backgrounds = [ # will take all background to compute background efficiency
    inFileDir + "TT_TuneCUETP8M1_13TeV-powheg-pythia8_Fall15MiniAODv2_v0.1.4+76X_HHAnalysis_2016-06-03.v0_histos.root",
    #inFileDir + "TT_FH_TuneCUETP8M1_13TeV-powheg-pythia8_Fall15MiniAODv2_v0.1.4+76X_HHAnalysis_2016-06-03.v0_histos.root",
    #inFileDir + "TT_FL_TuneCUETP8M1_13TeV-powheg-pythia8_Fall15MiniAODv2_v0.1.4+76X_HHAnalysis_2016-06-03.v0_histos.root",
    #inFileDir + "TT_SL_TuneCUETP8M1_13TeV-powheg-pythia8_Fall15MiniAODv2_v0.1.4+76X_HHAnalysis_2016-06-03.v0_histos.root",
    inFileDir + "ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg_Fall15MiniAODv2_v0.1.4+76X_HHAnalysis_2016-06-03.v0_histos.root",
    inFileDir + "ST_tW_top_5f_inclusiveDecays_13TeV-powheg_Fall15MiniAODv2_v0.1.4+76X_HHAnalysis_2016-06-03.v0_histos.root",
    inFileDir + "DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_extended_ext0_plus_ext1_plus_ext3_v0.1.4+76X_HHAnalysis_2016-06-03.v0_histos.root",
    inFileDir + "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_extended_ext0_plus_ext1_plus_ext4_v0.1.4+76X_HHAnalysis_2016-06-03.v0_histos.root",
    ]

variablesForRocCurves = [] #on each canvas, draw one rocCurve per variable
nodes_mva = ["SM", "2", "5", "6", "7", "12"]
date = "2016_07_05"
suffix = "VS_TT_DYHTonly_tW_8var"
bdtTemplate = "MVA_DATE_BDT_NODE_SUFFIX_All_hh_llmetjj_HWWleptons_btagM_csv_mll_cut"

# will make on canvas per signal
nodes_sig = nodes_mva
#nodes_sig.remove("all")

gStyle()
for node in nodes_sig:
    signal = inFileDir + "GluGluToHHTo2B2VTo2L2Nu_node_{}_13TeV-madgraph_v0.1.4+76X_HHAnalysis_2016-06-03.v0_histos.root".format(node)
    sigFile = R.TFile(signal)
    
    bkgFiles = []
    for background in backgrounds : 
        bkgFiles.append(R.TFile(background))
    
    bkgTH1 = {}
    sigTH1 = {}
    bkgEffVsCut = {}
    sigEffVsCut = {}
    Rocs = []
    merit = []
    leg = R.TLegend(0.51,0.19,0.943,0.49)
    leg2 = R.TLegend(0.21,0.59,0.643,0.89)
    
    for mva in nodes_mva:
        
        var = bdtTemplate.replace("DATE", date).replace("NODE", mva).replace("SUFFIX", suffix)
        print("Working on %r" % var)
        
        sigTH1[var] = sigFile.Get(var)
        bkgTH1[var] = bkgFiles[0].Get(var)
        for bkgFile in bkgFiles[1:]:
            bkgTH1[var].Add(bkgFile.Get(var))
        
        bkgEffVsCut[var] = drawEffVsCutCurve(bkgTH1[var])
        sigEffVsCut[var] = drawEffVsCutCurve(sigTH1[var])
        
        roc = drawROCfromEffVsCutCurves(sigEffVsCut[var], bkgEffVsCut[var])
        Rocs.append(roc)
        leg.AddEntry(roc, "BDT training: {}".format(mva), "L")

        sigTH1[var].Scale(1000)
        merit.append(drawFigMeritVsCutCurve(bkgTH1[var], sigTH1[var]))
        leg2.AddEntry(merit[-1], "BDT training: {}".format(mva), "L")
    
    drawTGraph(Rocs, "Signal_{}".format(node), "Background Efficiency", "Signal Efficiency", leg, "Signal: {}".format(node), "", ["pdf", "png", "root"], outFileDir, range=[[-0.05, 1.05], [-0.05, 1.05]], log_range=[[0.001, 1], [0.5, 1]])
    drawTGraph(merit, "Merit_signal_{}".format(node), "BDT output", "2 x (sqrt(S + B) - sqrt(B))", leg2, "Signal: {} (1 pb)".format(node), "", ["pdf", "png", "root"], outFileDir)

