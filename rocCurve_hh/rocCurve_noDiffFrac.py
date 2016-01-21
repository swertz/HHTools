import os, sys
import ROOT as R
sys.path.append("../../CommonTools/toolBox/")
from rocCurveFacility import *
from drawCanvas import *
R.gROOT.SetBatch()

inFileDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/CommonTools/histFactory/hists_skimmed_btagMM_bdtCut_2016_01_17/"

outFileDir = inFileDir +"rocCurve_" + sys.argv[1]
if not os.path.isdir(outFileDir):
    os.system("mkdir " + outFileDir)
print "Will write ROC curves in %s "%(outFileDir)


backgrounds = [ # will take all background to compute background efficiency
    inFileDir+"DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root",
    inFileDir+"DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root", 
    inFileDir+"TTTo2L2Nu_13TeV-powheg_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root", 
    #inFileDir+"VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root",
    inFileDir+"ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root", 
    inFileDir+"ST_tW_top_5f_inclusiveDecays_13TeV-powheg_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"    
    ]

variablesForRocCurves = [] #on each canvas, draw one rocCurve per variable
masses_var = ["400", "650", "900"]
spins_var = ["0","2"] 
date = "2016_01_17"
bdtTemplate = "MVA_DATE_BDT_XSPIN_MASS_SUFFIX"

suffix = "VS_TT1_DY0_8var_bTagMM"

masses_sig = ["400", "650", "900"]
spins_sig = ["0", "2"]
# will make on canvas per signal

gStyle()
for spin_sig in spins_sig :
    for mass_sig in masses_sig :
        if spin_sig == "0" :
            signal = inFileDir + "GluGluToRadionToHHTo2B2VTo2L2Nu_M-%s_narrow_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"%mass_sig
        else : 
            signal = inFileDir + "GluGluToBulkGravitonToHHTo2B2VTo2L2Nu_M-%s_narrow_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"%mass_sig
        sigFile = R.TFile(signal)
        bkgFiles = []
        for background in backgrounds : 
            bkgFiles.append(R.TFile(background))
        bkgTH1 = {}
        sigTH1 = {}
        bkgEffVsCut = {}
        sigEffVsCut = {}
        Rocs = []
        leg = R.TLegend(0.61,0.19,0.943,0.49)
        color = 2 
        marker = 20
        for mass_var in masses_var :
            for spin_var in spins_var : 
                var = bdtTemplate.replace("DATE", date).replace("SPIN", spin_var).replace("MASS", mass_var).replace("SUFFIX", suffix)
                sigTH1[var] = sigFile.Get(var)
                bkgTH1[var] = bkgFiles[0].Get(var)
                for bkgFile in bkgFiles[1:] :
                    bkgTH1[var].Add(bkgFile.Get(var))
                bkgEffVsCut[var] = drawEffVsCutCurve(bkgTH1[var])
                sigEffVsCut[var] = drawEffVsCutCurve(sigTH1[var])
                roc = drawROCfromEffVsCutCurves(sigEffVsCut[var], bkgEffVsCut[var])
                Rocs.append(roc)
                leg.AddEntry(roc, "X%s %s VS TT"%(spin_var, mass_var), "P")
        drawTGraph(Rocs, "Sample_X%s_%s"%(spin_sig, mass_sig), "Background Efficiency", "Signal Efficiency", leg, "Sample X%s %s"%(spin_sig, mass_sig), "", ["pdf", "png", "root"], outFileDir)

