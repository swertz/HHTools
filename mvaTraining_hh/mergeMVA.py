import os, sys
from trainMVA import *
from multiprocessing import Pool

#inFileDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/CommonTools/treeFactory/allFlavour_trigger_btagMM/condor/output/"
inFileDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/CommonTools/treeFactory/allFlavour_trigger_btagMM_2016_01_14/condor/output/"
outFileDir = inFileDir + "withMVAoutCorrect/"
#outFileDir = inFileDir + "/withMVAout_DYevtSum/"

filesForMerging  = [file for file in os.listdir(inFileDir) if "_histos.root" in file and not ("WJetsToLNu" in file or "M-650" in file or "M-400" in file or "M-900" in file or "DY" in file or "Run2015D" in file or "TTTo2L2Nu" in file or "VVTo2L2Nu" in file or "ST_tW" in file) and "ToHHTo2B" in file]
#xmlFileDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/CommonTools/mvaTraining/HHAnalysis/weights/"
xmlFileDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/HHTools/mvaTraining_hh/weights/"

massToMerge = ["400", "650", "900"]
spinToMerge = ["0", "2"]
list_dict_xmlFile_label = []
for massPoint in massToMerge :
    for spin in spinToMerge :
        tempdict = {}
        label = "2016_01_17_BDT_X%s_%s_VS_TT09_DY01_8var_bTagMM"%(spin, massPoint)
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
