import os, sys
from trainMVA import *
from multiprocessing import Pool

#inFileDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/CommonTools/treeFactory/allFlavour_trigger_btagMM/condor/output/"
#inFileDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/CommonTools/treeFactory/allFlavour_trigger_btagMM_2016_01_14/condor/output/"
inFileDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/HHTools/treeFactory_hh/2016-02-18/condor/output/"
outFileDir = inFileDir + "withMVAout/"
#outFileDir = inFileDir + "/withMVAout_DYevtSum/"

filesForMerging  = [file for file in os.listdir(inFileDir) if "_histos.root" in file and not ("WJetsToLNu" in file or "QCD" in file)]
#xmlFileDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/CommonTools/mvaTraining/HHAnalysis/weights/"
xmlFileDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/HHTools/mvaTraining_hh/weights/"

date = "2016_02_19"
suffix = "VS_TT_DYHTonly_tW_8var"  #DY_WoverSum_8var_bTagMM_noEvtW"
label_template = "DATE_BDT_XSPIN_MASS_SUFFIX"

massToMerge = ['350', '400', '500', '650']
spinToMerge = ["0"]
list_dict_xmlFile_label = []
for massPoint in massToMerge :
    for spin in spinToMerge :
        tempdict = {}
        label = "2016_02_19_BDT_X%s_%s_VS_TT_DYHTonly_tW_8var"%(spin, massPoint)
        tempdict["label"] = label
        tempdict["discriList"] = discriList
        tempdict["spectatorList"] = spectatorList
        tempdict["xmlFile"] = xmlFileDir+label+"_kBDT.weights.xml"
        list_dict_xmlFile_label.append(tempdict)
    
if not os.path.isdir(outFileDir):
    os.system("mkdir "+outFileDir)
print outFileDir

pool = Pool(15)
parametersForPool = []
for file in filesForMerging :
    parametersForPool.append([inFileDir, file, outFileDir, list_dict_xmlFile_label])
pool.map(MVA_out_in_tree, parametersForPool)
pool.close()
pool.join()
