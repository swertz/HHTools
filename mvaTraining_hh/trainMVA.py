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


date = "2016_02_19"
suffix = "VS_TT_DYHTonly_tW_8var"  #DY_WoverSum_8var_bTagMM_noEvtW"
label_template = "DATE_BDT_XSPIN_MASS_SUFFIX"

massPoints = ['400', '650'] #['350', '400', '500', '650']  #['400', '650'] #, '900']
spins = ["0"]
inFileDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/HHTools/treeFactory_hh/2016-02-18/condor/output/"

# SAMPLES FOR THE TRAINING

ttSample = "TTTo2L2Nu_13TeV-powheg_MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0"
ttDbSample = get_sample(unicode(ttSample))

DY50_HT100to200 = "DYJetsToLL_M-50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_Spring15MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0"
DY50_HT100to200_db = get_sample(unicode(DY50_HT100to200))

DY50_HT200to400 = "DYJetsToLL_M-50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_Spring15MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0"
DY50_HT200to400_db = get_sample(unicode(DY50_HT200to400))

DY50_HT400to600 = "DYJetsToLL_M-50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_Spring15MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0"
DY50_HT400to600_db = get_sample(unicode(DY50_HT400to600))

DY50_HT600toInf = "DYJetsToLL_M-50_HT-600toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_Spring15MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0"
DY50_HT600toInf_db = get_sample(unicode(DY50_HT600toInf))

DY5to50_HT100to200 = "DYJetsToLL_M-5to50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_Spring15MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0"
DY5to50_HT100to200_db = get_sample(unicode(DY5to50_HT100to200))

DY5to50_HT200to400 = "DYJetsToLL_M-5to50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_Spring15MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0"
DY5to50_HT200to400_db = get_sample(unicode(DY5to50_HT200to400))

DY5to50_HT400to600 = "DYJetsToLL_M-5to50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_Spring15MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0"
DY5to50_HT400to600_db = get_sample(unicode(DY5to50_HT400to600))

DY5to50_HT600toInf = "DYJetsToLL_M-5to50_HT-600toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_Spring15MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0"
DY5to50_HT600toInf_db = get_sample(unicode(DY5to50_HT600toInf))

ST_tw = "ST_tW_top_5f_inclusiveDecays_13TeV-powheg_MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0"
ST_tw_db = get_sample(unicode(ST_tw))
ST_tbarw = "ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg_MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0"
ST_tbarw_db = get_sample(unicode(ST_tbarw))

#dy10Sample = "DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX_MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0"
#dy10DbSample = get_sample(unicode(dy10Sample))
#dy50Sample = "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX_MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0"
#dy50DbSample = get_sample(unicode(dy50Sample))
bkgFiles = { 
        "TT" : { 
                    "files" : [inFileDir+ttSample+"_histos.root"],
                    "relativeWeight" : ttDbSample.source_dataset.xsection/ttDbSample.event_weight_sum
                },
        "DY50_HT100to200" : { 
                    "files" : [inFileDir+DY50_HT100to200+"_histos.root"],
                    "relativeWeight" : DY50_HT100to200_db.source_dataset.xsection/DY50_HT100to200_db.event_weight_sum
                },
        "DY50_HT200to400" : { 
                    "files" : [inFileDir+DY50_HT200to400+"_histos.root"],
                    "relativeWeight" : DY50_HT200to400_db.source_dataset.xsection/DY50_HT200to400_db.event_weight_sum
                },
        "DY50_HT400to600" : { 
                    "files" : [inFileDir+DY50_HT400to600+"_histos.root"],
                    "relativeWeight" : DY50_HT400to600_db.source_dataset.xsection/DY50_HT400to600_db.event_weight_sum
                },
        "DY50_HT600toInf" : { 
                    "files" : [inFileDir+DY50_HT600toInf+"_histos.root"],
                    "relativeWeight" : DY50_HT600toInf_db.source_dataset.xsection/DY50_HT600toInf_db.event_weight_sum
                },
        "DY5to50_HT100to200" : { 
                    "files" : [inFileDir+DY5to50_HT100to200+"_histos.root"],
                    "relativeWeight" : DY5to50_HT100to200_db.source_dataset.xsection/DY5to50_HT100to200_db.event_weight_sum
                },
        "DY5to50_HT200to400" : { 
                    "files" : [inFileDir+DY5to50_HT200to400+"_histos.root"],
                    "relativeWeight" : DY5to50_HT200to400_db.source_dataset.xsection/DY5to50_HT200to400_db.event_weight_sum
                },
        "DY5to50_HT400to600" : { 
                    "files" : [inFileDir+DY5to50_HT400to600+"_histos.root"],
                    "relativeWeight" : DY5to50_HT400to600_db.source_dataset.xsection/DY5to50_HT400to600_db.event_weight_sum
                },
        "DY5to50_HT600toInf" : { 
                    "files" : [inFileDir+DY5to50_HT600toInf+"_histos.root"],
                    "relativeWeight" : DY5to50_HT600toInf_db.source_dataset.xsection/DY5to50_HT600toInf_db.event_weight_sum
                },
        "ST_tw" : { 
                    "files" : [inFileDir+ST_tw+"_histos.root"],
                    "relativeWeight" : ST_tw_db.source_dataset.xsection/ST_tw_db.event_weight_sum
                },
        "ST_tbarw" : { 
                    "files" : [inFileDir+ST_tbarw+"_histos.root"],
                    "relativeWeight" : ST_tbarw_db.source_dataset.xsection/ST_tbarw_db.event_weight_sum
                },
        #"DY10-50" : { 
        #            "files" : [inFileDir+dy10Sample+"_histos.root"],
        #            "relativeWeight" : dy10DbSample.source_dataset.xsection/dy10DbSample.event_weight_sum
        #        },
        #"DY50" : { 
        #            "files" : [inFileDir+dy50Sample+"_histos.root"],
        #            "relativeWeight" : dy50DbSample.source_dataset.xsection/dy50DbSample.event_weight_sum
        #        }
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
        #"llmetjj_projMET",
        "llmetjj_MTformula"
        ]
spectatorList = []
cut = "(91 - ll_M) > 15 && ll_DR_l_l < 2.2 && jj_DR_j_j < 3.1 && llmetjj_DPhi_ll_jj > 1.5"
MVAmethods = ["kBDT"]
weightExpr = "event_weight * trigeff * jjbtag * llidiso * pu"

if __name__ == '__main__':
    for mass in massPoints :
        for spin in spins :
            if spin == "0" :
                sigFiles = {
                            "X%s_%s"%(spin, mass) : 
                            {
                                "files" : [inFileDir+"GluGluToRadionToHHTo2B2VTo2L2Nu_M-%s_narrow_MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0_histos.root"%mass],
                                "relativeWeight" : 1.
                            }
                        }
            elif spin == "2" : 
                sigFiles = {
                            "X%s_%s"%(spin, mass) : 
                            {
                                "files" : [inFileDir+"GluGluToBulkGravitonToHHTo2B2VTo2L2Nu_M-%s_narrow_MiniAODv2_v2.0.4+7415_HHAnalysis_2016-02-14.v0_histos.root"%mass],
                                "relativeWeight" : 1.
                            }
                        }
            else : 
                print "Spin choice has to be '0' or '2'."
            label = label_template.replace("DATE", date).replace("SPIN", spin).replace("MASS", mass).replace("SUFFIX", suffix)
            print bkgFiles, sigFiles
            trainMVA(bkgFiles, sigFiles, discriList, cut, weightExpr, MVAmethods, spectatorList, label)

