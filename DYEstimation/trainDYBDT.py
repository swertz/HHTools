#! /usr/bin/env python

import sys, os
import copy

sys.path.append("../../CommonTools/mvaTraining/")
from tmvaTools import *

sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/storm-0.20-py2.7-linux-x86_64.egg')
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/MySQL_python-1.2.3-py2.7-linux-x86_64.egg')

CMSSW_BASE = os.environ['CMSSW_BASE']
SCRAM_ARCH = os.environ['SCRAM_ARCH']
sys.path.append(os.path.join(CMSSW_BASE,'bin', SCRAM_ARCH))

from SAMADhi import Sample, DbStore

def get_sample(name):
    dbstore = DbStore()
    resultset = dbstore.find(Sample, Sample.name == name)
    return resultset.one()

date = "2017_02_17"
suffix = "bb_cc_vs_rest_10var"
label_template = "DATE_BDTDY_SUFFIX"

inFileDir = "/home/fynu/swertz/scratch/CMSSW_8_0_25/src/cp3_llbb/HHTools/condor/170217_skimDY_for_dy/condor/output/"

# SAMPLES FOR THE TRAINING

DYJetsToLL_M10to50 = "DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_extended_ext0_plus_ext1_v4.4.2+80X_HHAnalysis_2017-02-13.v2"
DYJetsToLL_M10to50_db = get_sample(unicode(DYJetsToLL_M10to50))

DYJetsToLL_M50_0J = "DYToLL_0J_13TeV-amcatnloFXFX-pythia8_extended_ext0_plus_ext1_v4.4.2+80X_HHAnalysis_2017-02-13.v2"
DYJetsToLL_M50_0J_db = get_sample(unicode(DYJetsToLL_M50_0J))
DYJetsToLL_M50_1J = "DYToLL_1J_13TeV-amcatnloFXFX-pythia8_extended_ext0_plus_ext1_v4.4.2+80X_HHAnalysis_2017-02-13.v2"
DYJetsToLL_M50_1J_db = get_sample(unicode(DYJetsToLL_M50_1J))
DYJetsToLL_M50_2J = "DYToLL_2J_13TeV-amcatnloFXFX-pythia8_extended_ext0_plus_ext1_v4.4.2+80X_HHAnalysis_2017-02-13.v2"
DYJetsToLL_M50_2J_db = get_sample(unicode(DYJetsToLL_M50_2J))

bkgFiles = { 
        "DYJetsToLL_M-10to50": {
                    "files": [ inFileDir + DYJetsToLL_M10to50 + "_histos.root" ],
                    "relativeWeight": DYJetsToLL_M10to50_db.source_dataset.xsection / DYJetsToLL_M10to50_db.event_weight_sum
                },
        "DYJetsToLL_M-50_0J": {
                    "files": [ inFileDir + DYJetsToLL_M50_0J + "_histos.root" ],
                    "relativeWeight": DYJetsToLL_M50_0J_db.source_dataset.xsection / DYJetsToLL_M50_0J_db.event_weight_sum
                },
        "DYJetsToLL_M-50_1J": {
                    "files": [ inFileDir + DYJetsToLL_M50_1J + "_histos.root" ],
                    "relativeWeight": DYJetsToLL_M50_1J_db.source_dataset.xsection / DYJetsToLL_M50_1J_db.event_weight_sum
                },
        "DYJetsToLL_M-50_2J": {
                    "files": [ inFileDir + DYJetsToLL_M50_2J + "_histos.root" ],
                    "relativeWeight": DYJetsToLL_M50_2J_db.source_dataset.xsection / DYJetsToLL_M50_2J_db.event_weight_sum
                },
        }

discriList = [
        "jet1_pt",
        "jet1_eta",
        "jet2_pt",
        "jet2_eta",
        "jj_pt",
        "ll_pt",
        "ll_eta",
        "llmetjj_DPhi_ll_met",
        "ht",
        "nJetsL"
        ]
#discriList = [
#        "jet1_pt",
#        "jet1_eta",
#        "jet2_pt",
#        "jet2_eta",
#        "jj_DPhi_j_j",
#        "ll_pt",
#        "ll_eta",
#        "llmetjj_DPhi_ll_jj",
#        "llmetjj_DPhi_ll_met",
#        "lljj_pt"
#    ]

spectatorList = []
cut = ""
MVAmethods = ["kBDT"]
weightExpr = "event_weight * trigeff * llidiso * pu * sample_weight"

sigFiles = copy.deepcopy(bkgFiles)

sigSelection = "(gen_bb || gen_cc)"
bkgSelection = "(!(gen_bb || gen_cc))"

label = label_template.replace("DATE", date).replace("SUFFIX", suffix)

if __name__ == "__main__":
    trainMVA(bkgFiles, sigFiles, discriList, cut, weightExpr, MVAmethods, spectatorList, label, sigWeightExpr=sigSelection, bkgWeightExpr=bkgSelection, nSignal=1000000, nBkg=1000000)
