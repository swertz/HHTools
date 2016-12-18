#! /usr/bin/env python

import sys, os

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


date = "2016_07_05"
suffix = "VS_TT_DYHTonly_tW_8var"
label_template = "DATE_BDT_NODE_SUFFIX"

# v1 training
#nodes = ["SM", "box", "5", "8", "13"] # v1 nodes for separate training
#nodes = ["2", "3", "4", "5", "7", "8", "9", "10", "11", "12", "13"] # v1 nodes for "all" training
#inFileDir = "/home/fynu/swertz/scratch/CMSSW_7_6_3_patch2/src/cp3_llbb/HHTools/condor/skim_160527_0/condor/output/"

# v2 training
nodes = ["SM", "2", "5", "6", "12"] # v1 nodes for separate training
#nodes = ["7"] # v1 nodes for separate training
#nodes = ["SM", "box", "1", "2", "3", "4", "5", "7", "8", "9", "10", "11", "12"] # v1 nodes for "all" training
inFileDir = "/home/fynu/sbrochet/scratch/Framework/CMSSW_7_6_5/src/cp3_llbb/HHTools/treeFactory_hh/160704_postpreapproval_newjer/condor/output/"

# SAMPLES FOR THE TRAINING

ttSample = "TT_TuneCUETP8M1_13TeV-powheg-pythia8_Fall15MiniAODv2_v0.1.4+76X_HHAnalysis_2016-06-03.v0"
ttDbSample = get_sample(unicode(ttSample))

DY50_incl = "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended_ext0_plus_ext1_v0.1.4+76X_HHAnalysis_2016-06-03.v0" 
DY50_incl_db = get_sample(unicode(DY50_incl))

DY50_HT100to200 = "DYJetsToLL_M-50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_Fall15MiniAODv2_v0.1.4+76X_HHAnalysis_2016-06-03.v0"
DY50_HT100to200_db = get_sample(unicode(DY50_HT100to200))

DY50_HT200to400 = "DYJetsToLL_M-50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_Fall15MiniAODv2_v0.1.4+76X_HHAnalysis_2016-06-03.v0"
DY50_HT200to400_db = get_sample(unicode(DY50_HT200to400))

DY50_HT400to600 = "DYJetsToLL_M-50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended_ext0_plus_ext1_v0.1.4+76X_HHAnalysis_2016-06-03.v0"
DY50_HT400to600_db = get_sample(unicode(DY50_HT400to600))

DY50_HT600toInf = "DYJetsToLL_M-50_HT-600toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended_ext0_plus_ext1_v0.1.4+76X_HHAnalysis_2016-06-03.v0"
DY50_HT600toInf_db = get_sample(unicode(DY50_HT600toInf))

DY5to50_incl = "DYJetsToLL_M-5to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_Fall15MiniAODv2_v0.1.4+76X_HHAnalysis_2016-06-03.v0" 
DY5to50_incl_db = get_sample(unicode(DY5to50_incl))

DY5to50_HT100to200 = "DYJetsToLL_M-5to50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended_ext0_plus_ext1_v0.1.4+76X_HHAnalysis_2016-06-03.v0"
DY5to50_HT100to200_db = get_sample(unicode(DY5to50_HT100to200))

DY5to50_HT200to400 = "DYJetsToLL_M-5to50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_Fall15MiniAODv2_v0.1.4+76X_HHAnalysis_2016-06-03.v0"
DY5to50_HT200to400_db = get_sample(unicode(DY5to50_HT200to400))

DY5to50_HT400to600 = "DYJetsToLL_M-5to50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_Fall15MiniAODv2_v0.1.4+76X_HHAnalysis_2016-06-03.v0"
DY5to50_HT400to600_db = get_sample(unicode(DY5to50_HT400to600))

DY5to50_HT600toInf = "DYJetsToLL_M-5to50_HT-600toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended_ext0_plus_ext1_v0.1.4+76X_HHAnalysis_2016-06-03.v0"
DY5to50_HT600toInf_db = get_sample(unicode(DY5to50_HT600toInf))

DYJetsToLL_M10to50 = "DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_extended_ext0_plus_ext1_plus_ext3_v0.1.4+76X_HHAnalysis_2016-06-03.v0"
DYJetsToLL_M10to50_db = get_sample(unicode(DYJetsToLL_M10to50))

DYJetsToLL_M50 = "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_extended_ext0_plus_ext1_plus_ext4_v0.1.4+76X_HHAnalysis_2016-06-03.v0"
DYJetsToLL_M50_db = get_sample(unicode(DYJetsToLL_M50))

ST_tw = "ST_tW_top_5f_inclusiveDecays_13TeV-powheg_Fall15MiniAODv2_v0.1.4+76X_HHAnalysis_2016-06-03.v0"
ST_tw_db = get_sample(unicode(ST_tw))
ST_tbarw = "ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg_Fall15MiniAODv2_v0.1.4+76X_HHAnalysis_2016-06-03.v0"
ST_tbarw_db = get_sample(unicode(ST_tbarw))

bkgFiles = { 
        "TT" : { 
                    "files" : [inFileDir+ttSample+"_histos.root"],
                    "relativeWeight" : ttDbSample.source_dataset.xsection/ttDbSample.event_weight_sum
                },
        #"DY50_incl" : { 
        #            "files" : [inFileDir+DY50_incl+"_histos.root"],
        #            "relativeWeight" : DY50_incl_db.source_dataset.xsection/DY50_incl_db.event_weight_sum
        #        },
        #"DY50_HT100to200" : { 
        #            "files" : [inFileDir+DY50_HT100to200+"_histos.root"],
        #            "relativeWeight" : DY50_HT100to200_db.source_dataset.xsection/DY50_HT100to200_db.event_weight_sum
        #        },
        #"DY50_HT200to400" : { 
        #            "files" : [inFileDir+DY50_HT200to400+"_histos.root"],
        #            "relativeWeight" : DY50_HT200to400_db.source_dataset.xsection/DY50_HT200to400_db.event_weight_sum
        #        },
        #"DY50_HT400to600" : { 
        #            "files" : [inFileDir+DY50_HT400to600+"_histos.root"],
        #            "relativeWeight" : DY50_HT400to600_db.source_dataset.xsection/DY50_HT400to600_db.event_weight_sum
        #        },
        #"DY50_HT600toInf" : { 
        #            "files" : [inFileDir+DY50_HT600toInf+"_histos.root"],
        #            "relativeWeight" : DY50_HT600toInf_db.source_dataset.xsection/DY50_HT600toInf_db.event_weight_sum
        #        },
        ##"DY5to50_incl" : { 
        ##            "files" : [inFileDir+DY5to50_incl+"_histos.root"],
        ##            "relativeWeight" : DY5to50_incl_db.source_dataset.xsection/DY5to50_incl_db.event_weight_sum
        ##        },
        #"DY5to50_HT100to200" : { 
        #            "files" : [inFileDir+DY5to50_HT100to200+"_histos.root"],
        #            "relativeWeight" : DY5to50_HT100to200_db.source_dataset.xsection/DY5to50_HT100to200_db.event_weight_sum
        #        },
        #"DY5to50_HT200to400" : { 
        #            "files" : [inFileDir+DY5to50_HT200to400+"_histos.root"],
        #            "relativeWeight" : DY5to50_HT200to400_db.source_dataset.xsection/DY5to50_HT200to400_db.event_weight_sum
        #        },
        #"DY5to50_HT400to600" : { 
        #            "files" : [inFileDir+DY5to50_HT400to600+"_histos.root"],
        #            "relativeWeight" : DY5to50_HT400to600_db.source_dataset.xsection/DY5to50_HT400to600_db.event_weight_sum
        #        },
        #"DY5to50_HT600toInf" : { 
        #            "files" : [inFileDir+DY5to50_HT600toInf+"_histos.root"],
        #            "relativeWeight" : DY5to50_HT600toInf_db.source_dataset.xsection/DY5to50_HT600toInf_db.event_weight_sum
        #        },
        "DYJetsToLL_M-10to50": {
                    "files": [inFileDir+DYJetsToLL_M10to50+"_histos.root"],
                    "relativeWeight": DYJetsToLL_M10to50_db.source_dataset.xsection/DYJetsToLL_M10to50_db.event_weight_sum
                },
        "DYJetsToLL_M-50": {
                    "files": [inFileDir+DYJetsToLL_M50+"_histos.root"],
                    "relativeWeight": DYJetsToLL_M50_db.source_dataset.xsection/DYJetsToLL_M50_db.event_weight_sum
                },
        "ST_tw" : { 
                    "files" : [inFileDir+ST_tw+"_histos.root"],
                    "relativeWeight" : ST_tw_db.source_dataset.xsection/ST_tw_db.event_weight_sum
                },
        "ST_tbarw" : { 
                    "files" : [inFileDir+ST_tbarw+"_histos.root"],
                    "relativeWeight" : ST_tbarw_db.source_dataset.xsection/ST_tbarw_db.event_weight_sum
                },
        }

print bkgFiles

discriList = [
        "jj_pt",
        "ll_pt",
        "ll_M",
        "ll_DR_l_l",
        "jj_DR_j_j",
        "llmetjj_DPhi_ll_jj",
        "llmetjj_minDR_l_j",
        "llmetjj_MTformula"
        ]

spectatorList = []
cut = "(91 - ll_M) > 15"
MVAmethods = ["kBDT"]
weightExpr = "event_weight * trigeff * jjbtag * llidiso * pu * sample_weight"

if __name__ == '__main__':
    for node in nodes:
        sigFiles = {}
        sigFiles[node] = {
                "files" : [ inFileDir + "GluGluToHHTo2B2VTo2L2Nu_node_{}_13TeV-madgraph_v0.1.4+76X_HHAnalysis_2016-06-03.v0_histos.root".format(node) ],
                "relativeWeight" : 1.
                }
        label = label_template.replace("DATE", date).replace("NODE", str(node)).replace("SUFFIX", suffix)
        trainMVA(bkgFiles, sigFiles, discriList, cut, weightExpr, MVAmethods, spectatorList, label)

    #sigFiles = {}
    #for node in nodes:
        #sigFiles[node] = {
                            #"files" : [ inFileDir + "GluGluToHHTo2B2VTo2L2Nu_node_{}_13TeV-madgraph_v0.1.3+76X_HHAnalysis_2016-06-03.v0_histos.root".format(node) ], # v3
                            ##"files" : [ inFileDir + "GluGluToHHTo2B2VTo2L2Nu_node_{}_13TeV-madgraph_v0.1.4+76X_HHAnalysis_2016-06-03.v0_histos.root".format(node) ], # v1
                            #"relativeWeight" : 1.
                        #}
    #label = label_template.replace("DATE", date).replace("NODE", "all").replace("SUFFIX", suffix)
    #print bkgFiles, sigFiles
    #trainMVA(bkgFiles, sigFiles, discriList, cut, weightExpr, MVAmethods, spectatorList, label)
