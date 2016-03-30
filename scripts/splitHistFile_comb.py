import ROOT as R
import yaml
import copy

yamlDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/HHTools/plotIt_hh/forBDTREGIONS/"
yamlTemplate = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/HHTools/plotIt_hh/forBDTREGIONS/template.yml"

yamlFileTemplate = {"type" : "signal", "line-type" : 1, "line-width" : 2, "line-color" : "COLOR", "legend": "LEGEND"}

def splitHistFile(pairList_color, baseDir, rootFileName):
    fileIn = R.TFile(baseDir+rootFileName)
    keys = fileIn.GetListOfKeys()
    yamlName = yamlDir+rootFileName.replace(".root",".yml")
    yamlOut = open(yamlName, 'w')
    for pair in pairList_color.keys():
        print "\tTreating ",pair, " order."
        fileOutName = rootFileName.replace(".root", "_"+pair+"Odered.root")
        fileOut = R.TFile(baseDir + fileOutName, "recreate")
        for key in keys :
            keyName = key.GetName()
            if pair+"Ordered" in keyName :
                th1 = fileIn.Get(keyName)
                th1.SetName(keyName.replace("_"+pair+"Ordered", ""))
                th1.Write()
        fileOut.Close()
        print "\t", fileOutName, " written."
        yamlFileAttr = copy.deepcopy(yamlFileTemplate)
        yamlFileAttr["line-color"] = pairList_color[pair]
        yamlFileAttr["legend"] = pair
        yamlFile = {fileOutName : yamlFileAttr}
        yamlOut.write(yaml.dump(yamlFile, default_flow_style=False))
    yamlOut.close()
    print "\t", yamlName, " written.\n"


pairList_color = {"csv" : "#4000ff", "ht" : "#ff4000", "pt" : "#40ff00", "mh" : "#000000", "ptOverM" : "#800000"} # MC Truth : "#000000", "pt" : #40ff00
#baseDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/CommonTools/histFactory/hists_LLLL_jetidL_csvANDhtOrdered/condor/output/"
baseDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/CommonTools/histFactory/hists_TTTT_jetidL_combStud/condor/output/"
rootFileNames = [
        "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX_MiniAODv2_v1.0.0+7415_HHAnalysis_2015-10-20.v4_histos.root", 
        "GluGluToRadionToHHTo2B2VTo2L2Nu_M-400_narrow_MiniAODv2_v1.0.0+7415_HHAnalysis_2015-10-20.v4_histos.root", 
        "GluGluToRadionToHHTo2B2VTo2L2Nu_M-650_narrow_MiniAODv2_v1.0.0+7415_HHAnalysis_2015-10-20.v4_histos.root", 
        "GluGluToRadionToHHTo2B2VTo2L2Nu_M-900_narrow_MiniAODv2_v1.0.0+7415_HHAnalysis_2015-10-20.v4_histos.root", 
        "TT_TuneCUETP8M1_13TeV-powheg-pythia8_MiniAODv2_v1.0.0+7415_HHAnalysis_2015-10-20.v4_histos.root"
        ]
print baseDir, "\n"
for rootFileName in rootFileNames : 
    print "Splitting ", rootFileName
    splitHistFile(pairList_color, baseDir, rootFileName)

