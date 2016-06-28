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
sys.path.append(os.path.join(CMSSW_BASE,'bin', SCRAM_ARCH))
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
    1658, # tW 
    1666, # tW
    1715, # sT t-chan
    1718, # TT incl NLO
    1733, # DY M10-50 NLO merged
    1734, # DY M-50 NLO merged 
    ])

# DY LO
IDs.extend([
    # M-50 incl. merged
    1739,
    # M-50, binned HT > 100
    1731,
    1679,
    1736,
    1737,
    # M-5to50 incl.: forget it...
    1717,
    # M-5to50, binned HT
    1738,
    1705,
    1680,
    1735,
    ])
#
# Other backgrounds
# VV
IDs.extend([
    #1624, # VV(2L2Nu)
    
    1691, # WW(LNuQQ)
    1703, # WW(2L2Nu)
    
    1615, # WZ(3LNu)
    1701, # WZ(L3Nu)
    1721, # WZ(LNu2Q)
    1725, # WZ(2L2Q)
    
    1723, # ZZ(4L)
    1727, # ZZ(2L2Nu)
    1729, # ZZ(2L2Q)
    
    1633, # WZZ
    ])

# Higgs
IDs.extend([
    # ggH ==> no H(ZZ)?
    1650, # H(WW(2L2Nu))
    1656, # H(BB)

    # ZH
    1616, # ggZ(LL)H(WW(2L2Nu))
    1653, # ZH(WW)
    1628, # ggZ(LL)H(BB)
    1644, # Z(LL)H(BB)
    1657, # ggZ(NuNu)H(BB)
    
    # VBF
    1629, # VBFH(BB)
    1690, # VBFH(WW(2L2Nu))

    # WH
    1643, # W+(LNu)H(BB)
    1692, # W-(LNu)H(BB)
    1659, # W+H(WW)
    1664, # W-H(WW)

    # bbH
    1687, # bbH(BB) ybyt
    1641, # bbH(BB) yb2
    ])

# Top
IDs.extend([
    1688, # sT s-channel
    1622, # TTW(LNu)
    1675, # TTW(QQ)
    1693, # TTZ(2L2Nu)
    1702, # TTZ(QQ),
    1694, # ttH(bb)
    1710, # ttH(nonbb)
    #1711, # TT(2L2Nu)
    ])

# Wjets
IDs.extend([
    1648, # JetsLNu
    1780, 1781, 1782, 1783, 1784, 1785, 1786, # HT binned
    ])

## QCD ==> 30to50 missing
#IDs.extend([
#    1661, # Pt-15to20EMEnriched
#    1671, # Pt-20to30EMEnriched
#    1681, # Pt-50to80EMEnriched
#    1637, # Pt-80to120EMEnriched
#    1632, # Pt-120to170EMEnriched
#    1670, # Pt-170to300EMEnriched
#    1645, # Pt-300toInfEMEnriched
#    #1719, # Pt-20toInfMuEnriched
#    ])

# Resonant
#IDs.extend([1617, 1625, 1630, 1631, 1638, 1640, 1647, 1652, 1654, 1660, 1665, 1668, 1669, 1674, 1676, 1678, 1685, 1686, 1689, 1695, 1699, 1700, 1704, 1706, 1708, 1728])

# NonResonant
#IDs.extend([
#    #1651, # SM
#    1672, # box
#    ])
#IDs.extend([1614, 1618, 1626, 1634, 1635, 1639, 1673, 1677, 1684, 1697, 1698, 1722])

# NonResonant with GEN info
IDs.extend([
    1765, # SM
    1760, # box
    ])
#IDs.extend([1792, 1767, 1748, 1763, 1753, 1757, 1764, 1756, 1759, 1751, 1755, 1762])

# NonResonant merged
IDs.append(1769)

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
sample = get_sample(1769)
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
        filesperJob = 1
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

## Modify the input samples to add sample cuts and stuff
if args.filter: 
    for sample in mySub.sampleCfg[:]:
        # TTbar final state splitting
        if 'TT_TuneCUETP8M1_13TeV-powheg-pythia8_Fall15MiniAODv2' in sample["db_name"]:

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

        # Handle the cluster v1tov3 reweighting
        if "all_nodes" in sample["db_name"]:
            ## For v1->v1 reweighting check:
            #for node in range(2, 14):
            #    node_str = "node_rwgt_" + str(node)
            for node in range(1, 13):
                newSample = copy.deepcopy(sample)
                newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])
                
                node_str = "node_" + str(node)
                newSample["db_name"] = sample["db_name"].replace("all_nodes", node_str)
                newJson["sample-weight"] = "cluster_" + node_str
                
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
