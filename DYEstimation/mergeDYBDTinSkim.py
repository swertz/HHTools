#! /usr/bin/env python

import os, sys
import trainDYBDT
from multiprocessing import Pool

inFileDir = "/home/fynu/swertz/scratch/CMSSW_8_0_25/src/cp3_llbb/HHTools/condor/170217_skimDY_for_dy/condor/output/"

filesForMerging  = [ file for file in os.listdir(inFileDir) if "_histos.root" in file ]
xmlFileDir = "/home/fynu/swertz/scratch/CMSSW_8_0_25/src/cp3_llbb/HHTools/DYEstimation/weights/"

date = "2016_12_17"
suffix = "bb_cc_vs_rest_7var_ht_nJets"

label_template = "DATE_BDTDY_SUFFIX"
label = label_template.replace("DATE", date).replace("SUFFIX", suffix)

# Retrieve the variables directly from the training script - careful!
list_dict_xmlFile_label = [
        {
            "label": label,
            "discriList": trainDYBDT.discriList,
            "spectatorList": trainDYBDT.spectatorList,
            "xmlFile": xmlFileDir + label + "_kBDT.weights.xml",
        },
    ]

outFileDir = inFileDir + "withMVAout_" + label
if not os.path.isdir(outFileDir):
    os.system("mkdir " + outFileDir)
print outFileDir

pool = Pool(4)
parametersForPool = []
for file in filesForMerging :
    parametersForPool.append([inFileDir, file, outFileDir, list_dict_xmlFile_label])
pool.map(trainDYBDT.MVA_out_in_tree, parametersForPool)
pool.close()
pool.join()
