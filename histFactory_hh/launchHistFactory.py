#!/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/bin/python

# usage dans histfactory_hh : python launchHistFactory.py outputName [submit]

import sys, os, json
sys.path.append("../../CommonTools/histFactory/")
import copy
import datetime

import argparse

from condorTools import condorSubmitter

# Add default ingrid storm package
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/storm-0.20-py2.7-linux-x86_64.egg')
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/MySQL_python-1.2.3-py2.7-linux-x86_64.egg')

CMSSW_BASE = os.environ['CMSSW_BASE']
SCRAM_ARCH = os.environ['SCRAM_ARCH']
sys.path.append(os.path.join(CMSSW_BASE, 'bin', SCRAM_ARCH))
from SAMADhi import Dataset, Sample, DbStore

def get_sample(iSample):
    dbstore = DbStore()
    resultset = dbstore.find(Sample, Sample.sample_id == iSample)
    return resultset.one()

IDs = []
IDsToSplitMore = []

# Data
IDs.extend([
    1642, # DoubleEG
    1662, # MuonEG
    1716, # DoubleMuon
    ])

# Main backgrounds:
IDs.extend([
    1817, # tW top
    1846, # tW atop
    1894, # sT t-chan
    1909, # TT incl NLO
    1915, # DY M10-50 NLO merged
    1918, # DY M-50 NLO merged 
    ])

# DY LO
IDs.extend([
    # M-50 incl. merged
    1920,
    # M-50, binned HT > 100
    1884, # 100-200 non-merged
    1848, # 200-400 non-merged
    1917, # 400-600 merged
    1919, # 600-Inf merged
    # M-5to50 incl.: forget it...
    1878,
    # M-5to50, binned HT
    1916, # 100-200 merged
    1815, # 200-400 non-merged
    1824, # 400-600 non-merged
    1914, # 600-Inf merged
    ])
#
# Other backgrounds
# VV
IDs.extend([
    #1624, # VV(2L2Nu)
    
    1897, # WW(LNuQQ)
    1892, # WW(2L2Nu)
    
    1899, # WZ(3LNu)
    1838, # WZ(L3Nu)
    1908, # WZ(LNu2Q)
    1902, # WZ(2L2Q)
    
    1834, # ZZ(4L)
    1893, # ZZ(2L2Nu)
    1896, # ZZ(2L2Q)
    
    1872, # WZZ
    ])

# Higgs
IDs.extend([
    # ggH ==> no H(ZZ)?
    1844, # H(WW(2L2Nu))
    1849, # H(BB)

    # ZH
    1847, # ggZ(LL)H(WW(2L2Nu))
    1821, # ZH(WW)
    1866, # ggZ(LL)H(BB)
    1828, # Z(LL)H(BB)
    1883, # ggZ(NuNu)H(BB)
    
    # VBF
    1833, # VBFH(BB)
    1901, # VBFH(WW(2L2Nu))

    # WH
    1875, # W+(LNu)H(BB)
    1854, # W-(LNu)H(BB)
    1862, # W+H(WW)
    1858, # W-H(WW)

    # bbH
    1869, # bbH(BB) ybyt
    1874, # bbH(BB) yb2
    1841, # bbH(WW) ybyt
    1819, # bbH(WW) yb2
    ])

# Top
IDs.extend([
    1837, # sT s-channel
    1818, # TTW(LNu)
    1831, # TTW(QQ)
    1863, # TTZ(2L2Nu)
    1880, # TTZ(QQ),
    1839, # ttH(bb)
    1906, # ttH(nonbb)
    #1711, # TT(2L2Nu)
    ])

# # TT aMC@NLO
# IDs.append(1929)

# Wjets
IDs.extend([
    1876, # JetsLNu

    # HT binned
    1904, # 200-400
    1825, # 800-1200
    1907, # 1200 - 2500
    1898, # 2500 - Inf 
    ])

# QCD ==> 30to50 missing
# IDs.extend([
   # 1661, # Pt-15to20EMEnriched
   # 1671, # Pt-20to30EMEnriched
   # 1681, # Pt-50to80EMEnriched
   # 1637, # Pt-80to120EMEnriched
   # 1632, # Pt-120to170EMEnriched
   # 1670, # Pt-170to300EMEnriched
   # 1645, # Pt-300toInfEMEnriched
   # #1719, # Pt-20toInfMuEnriched
   # ])

# NonResonant with GEN info
IDsToSplitMore.extend([
    1927, # SM
    1928, # box
    ])

# NonResonant merged
IDsToSplitMore.append(1903)

parser = argparse.ArgumentParser(description='Facility to submit histFactory jobs on condor.')
parser.add_argument('-o', '--output', dest='output', default=str(datetime.date.today()), help='Name of the output directory.')
parser.add_argument('-s', '--submit', help='Choice to actually submit the jobs or not.', action="store_true")
parser.add_argument('-f', '--filter', dest='filter', default=True, help='Apply filter on DY ht.')
parser.add_argument('-t', '--test', help='Run on the output of HHAnalyzer not yet in the DB.', action="store_true")
parser.add_argument('-p', '--plotter', dest='plotter', default="generatePlots.py", help='Code generating the plots.')
parser.add_argument('-r', '--remove', help='Overwrite output directory if it already exists.', action="store_true")
parser.add_argument('--skip', help='Skip the building part.', action="store_true")
parser.add_argument('--tree', dest='treeFactory', action='store_true', default=False, help='Use treeFactory instead of histFactory')

args = parser.parse_args()

# get one of the new samples with gen info to read Tree structure
sample = get_sample(1903)
files = ["/storage/data/cms/" + x.lfn for x  in sample.files]

if args.test: 
    jsonName = "jsonTest.json"
    jsonFile = open(jsonName)
    datasetDict = json.load(jsonFile)
    for datasetName in datasetDict.keys():
        rootFileName = datasetDict[datasetName]["files"][0]
        break

samples = []
for ID in IDs + IDsToSplitMore:
    filesperJob = 15
    if ID in IDsToSplitMore:
        filesperJob = 100
    samples.append(
        {
            "ID": ID,
            "files_per_job": filesperJob,
        }
    )

if args.remove :
    if os.path.isdir(args.output):
        print "Are you sure you want to execute the following command ?"
        print "rm -r " + args.output
        print "Type enter if yes, ctrl-c if not."
        raw_input()
        os.system("rm -r " + args.output)
        print "Deleted ", args.output, " folder."

## Use treeFactory or histFactory

toolDir = "histFactory"
toolScript = "createPlotter.sh"
executable = "plotter.exe"

if args.treeFactory: 
    toolDir = "treeFactory"
    executable = "skimmer.exe"
    toolScript = "createSkimmer.sh"

if not args.skip :
    if args.test : 
        os.system(os.path.join("../../", "CommonTools", toolDir, "build", toolScript) + " %s %s %s"%(rootFileName, args.plotter, args.output))
    else : 
        os.system(os.path.join("../../", "CommonTools", toolDir, "build", toolScript) + " %s %s %s"%(files[0], args.plotter, args.output))


## Create Condor submitter to handle job creating
mySub = condorSubmitter(samples, "%s/build/" % args.output + executable, "DUMMY", args.output+"/", rescale = True)

## Create test_condor directory and subdirs
mySub.setupCondorDirs()

splitTT = False

## Modify the input samples to add sample cuts and stuff
if args.filter: 
    for sample in mySub.sampleCfg[:]:
        # TTbar final state splitting
        if splitTT and 'TT_TuneCUETP8M1_13TeV-powheg-pythia8_Fall15MiniAODv2' in sample["db_name"]:

            # Fully leptonic
            tt_fl_sample = copy.deepcopy(sample)
            newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])
            
            tt_fl_sample["db_name"] = sample["db_name"].replace("TT_Tune", "TT_FL_Tune")
            newJson["sample_cut"] = "(hh_gen_ttbar_decay_type >= 4 && hh_gen_ttbar_decay_type <= 10 && hh_gen_ttbar_decay_type != 7)"
            
            tt_fl_sample["json_skeleton"][tt_fl_sample["db_name"]] = newJson
            tt_fl_sample["json_skeleton"].pop(sample["db_name"])
            mySub.sampleCfg.append(tt_fl_sample)

            # Semi leptonic
            tt_sl_sample = copy.deepcopy(sample)
            newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])
            
            tt_sl_sample["db_name"] = sample["db_name"].replace("TT_Tune", "TT_SL_Tune")
            newJson["sample_cut"] = "(hh_gen_ttbar_decay_type == 2 || hh_gen_ttbar_decay_type == 3 || hh_gen_ttbar_decay_type == 7)"
            
            tt_sl_sample["json_skeleton"][tt_sl_sample["db_name"]] = newJson
            tt_sl_sample["json_skeleton"].pop(sample["db_name"])
            mySub.sampleCfg.append(tt_sl_sample)

            # Fully hadronic
            tt_fh_sample = copy.deepcopy(sample)
            newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])
            
            tt_fh_sample["db_name"] = sample["db_name"].replace("TT_Tune", "TT_FH_Tune")
            newJson["sample_cut"] = "(hh_gen_ttbar_decay_type == 1)"
            
            tt_fh_sample["json_skeleton"][tt_fh_sample["db_name"]] = newJson
            tt_fh_sample["json_skeleton"].pop(sample["db_name"])
            mySub.sampleCfg.append(tt_fh_sample)

            mySub.sampleCfg.remove(sample)

        # Merging with HT binned sample: add cut on inclusive one
        if 'DYJetsToLL_M-5to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' in sample["db_name"] or 'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' in sample["db_name"]: 
            sample["json_skeleton"][sample["db_name"]]["sample_cut"] = "event_ht < 100"

        if 'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8' in sample["db_name"]:
            sample["json_skeleton"][sample["db_name"]]["sample_cut"] = "event_ht < 100"

        # Handle the cluster reweighting
        if "all_nodes" in sample["db_name"]:
            ## For v1->v1 reweighting check:
            #for node in range(2, 14):
            #    node_str = "node_rwgt_" + str(node)
            #for node in range(1, 13):

            #    newSample = copy.deepcopy(sample)
            #    newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])
            #    
            #    node_str = "node_" + str(node)
            #    newSample["db_name"] = sample["db_name"].replace("all_nodes", node_str)
            #    newJson["sample-weight"] = "cluster_" + node_str
            #    
            #    newSample["json_skeleton"][newSample["db_name"]] = newJson
            #    newSample["json_skeleton"].pop(sample["db_name"])
            #    mySub.sampleCfg.append(newSample)
            
            # 1507 points
            for node in range(0, 1507):
                # Skip dummy Xanda
                if node in [324, 910, 985, 990]: continue

                newSample = copy.deepcopy(sample)
                newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])
                
                node_str = "point_" + str(node)
                newSample["db_name"] = sample["db_name"].replace("all_nodes", node_str)
                newJson["sample-weight"] = node_str
                
                newSample["json_skeleton"][newSample["db_name"]] = newJson
                newSample["json_skeleton"].pop(sample["db_name"])
                mySub.sampleCfg.append(newSample)

            mySub.sampleCfg.remove(sample)

## Write command and data files in the condor directory
mySub.createCondorFiles()

# Actually submit the jobs
# It is recommended to do a dry-run first without submitting to condor
if args.submit: 
   mySub.submitOnCondor()
