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


date = "2016_01_28"
suffix = "VS_TT09_DY01_WoverSum_8var_bTagMM"
label_template = "DATE_BDT_XSPIN_MASS_SUFFIX"

massPoints = ['400', '650', '900']
spins = ["0", "2"]
inFileDir = "/home/fynu/bfrancois/scratch/framework/oct2015/CMSSW_7_4_15/src/cp3_llbb/CommonTools/treeFactory/allFlavour_trigger_btagMM_2016_01_14/condor/output/"
ttSample = "TTTo2L2Nu_13TeV-powheg_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0"
ttDbSample = get_sample(unicode(ttSample))
dy10Sample = "DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0"
dy10DbSample = get_sample(unicode(dy10Sample))
dy50Sample = "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0"
dy50DbSample = get_sample(unicode(dy50Sample))
bkgFiles = { 
        "TT" : { 
                    "files" : [inFileDir+ttSample+"_histos.root"],
                    "relativeWeight" : ttDbSample.source_dataset.xsection/ttDbSample.event_weight_sum
                },
        "DY10-50" : { 
                    "files" : [inFileDir+dy10Sample+"_histos.root"],
                    "relativeWeight" : dy10DbSample.source_dataset.xsection/dy10DbSample.event_weight_sum
                },
        "DY50" : { 
                    "files" : [inFileDir+dy50Sample+"_histos.root"],
                    "relativeWeight" : dy50DbSample.source_dataset.xsection/dy50DbSample.event_weight_sum
                }
        }
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
cut = "(91.1876 - ll_M) > 15 && ll_DR_l_l < 2.2 && jj_DR_j_j < 3.1 && llmetjj_DPhi_ll_jj > 1.5"
MVAmethods = ["kBDT"]
weightExpr = "event_weight*ll_scaleFactor*jj_scaleFactor"

if __name__ == '__main__':
    for mass in massPoints :
        for spin in spins :
            if spin == "0" :
                sigFiles = {
                            "X%s_%s"%(spin, mass) : 
                            {
                                "files" : [inFileDir+"GluGluToRadionToHHTo2B2VTo2L2Nu_M-%s_narrow_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"%mass],
                                "relativeWeight" : 1.
                            }
                        }
            elif spin == "2" : 
                sigFiles = {
                            "X%s_%s"%(spin, mass) : 
                            {
                                "files" : [inFileDir+"GluGluToBulkGravitonToHHTo2B2VTo2L2Nu_M-%s_narrow_MiniAODv2_v1.2.0+7415_HHAnalysis_2016-01-11.v0_histos.root"%mass],
                                "relativeWeight" : 1.
                            }
                        }
            else : 
                print "Spin choice has to be '0' or '2'."
            label = label_template.replace("DATE", date).replace("SPIN", spin).replace("MASS", mass).replace("SUFFIX", suffix)
            label = "2016_01_17_BDT_X%s_%s_VS_TT09_DY01_8var_bTagMM"%(spin, mass)
            print bkgFiles, sigFiles
            trainMVA(bkgFiles, sigFiles, discriList, cut, weightExpr, MVAmethods, spectatorList, label)

