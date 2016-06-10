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
IDsToSplitLitleMore = []

## Data
#IDs.extend([
#    1642, # DoubleEG
#    1662, # MuonEG
#    1716, # DoubleMuon
#    ])
#
## Main backgrounds:
IDs.extend([
    1658, # tW 
    1666, # tW
    1715, # sT t-chan
    1718, # TT incl NLO
    1733, # DY M10-50 NLO merged
    1734, # DY M-50 NLO merged 
    ])

### DY LO
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
#IDs.extend([
#    #1624, # VV(2L2Nu)
#    
#    1691, # WW(LNuQQ)
#    1703, # WW(2L2Nu)
#    
#    1615, # WZ(3LNu)
#    1701, # WZ(L3Nu)
#    1721, # WZ(LNu2Q)
#    1725, # WZ(2L2Q)
#    
#    1723, # ZZ(4L)
#    1727, # ZZ(2L2Nu)
#    1729, # ZZ(2L2Q)
#    
#    1633, # WZZ
#    ])
#
## Higgs
#IDs.extend([
#    # ggH ==> no H(ZZ)?
#    1650, # H(WW(2L2Nu))
#    1656, # H(BB)
#
#    # ZH
#    1616, # ggZ(LL)H(WW(2L2Nu))
#    1653, # ZH(WW)
#    1628, # ggZ(LL)H(BB)
#    1644, # Z(LL)H(BB)
#    1657, # Z(NuNu)H(BB)
#    
#    # VBF
#    1629, # VBFH(BB)
#    1690, # VBFH(WW(2L2Nu))
#
#    # WH
#    1643, # W+(LNu)H(BB)
#    1692, # W-(LNu)H(BB)
#    1659, # W+H(WW)
#    1664, # W-H(WW)
#
#    # bbH
#    1687, # bbH(BB) ybyt
#    1641, # bbH(BB) yb2
#    ])
#
## Wjets
#IDs.extend([
#    1648, # JetsLNu
#    ])
#
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
#
## Top
#IDs.extend([
#    1688, # sT s-channel
#    1622, # TTW(LNu)
#    1675, # TTW(QQ)
#    1693, # TTZ(2L2Nu)
#    1702, # TTZ(QQ),
#    1694, # ttH(bb)
#    1710, # ttH(nonbb)
#    #1711, # TT(2L2Nu)
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
#IDs.extend([1768, 1767, 1748, 1763, 1753, 1757, 1764, 1756, 1759, 1751, 1755, 1762])

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

sample = get_sample(1769)
files = ["/storage/data/cms/" + x.lfn for x  in sample.files]

if args.test : 
    jsonName = "jsonTest.json"
    jsonFile = open(jsonName)
    datasetDict = json.load(jsonFile)
    for datasetName in datasetDict.keys() :
        rootFileName = datasetDict[datasetName]["files"][0]
        break

samples = []
for ID in IDs:
    filesperJob = 7
    if ID in IDsToSplitMore :
        filesperJob = 5
    if ID in IDsToSplitLitleMore :
        filesperJob = 2
    samples.append(
        {
            "ID": ID,
            "files_per_job": filesperJob,
        }
    )

if args.remove :
    if os.path.isdir(args.output) :
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

mySub = condorSubmitter(samples, "%s/build/" % args.output + executable, "DUMMY", args.output+"/", rescale = True)

## Create test_condor directory and subdirs
mySub.setupCondorDirs()

## Write command and data files in the condor directory
mySub.createCondorFiles()

## Modifies the input sample jsons to add sample cuts
if args.filter : 
    jsonSampleFileList = [os.path.join(mySub.inDir,jsonSampleFile) for jsonSampleFile in os.listdir(mySub.inDir) if "sample" in jsonSampleFile]
    for jsonSampleFilePath in jsonSampleFileList : 
        with open(jsonSampleFilePath, 'r') as jsonSampleFile :
            jsonSample = json.load(jsonSampleFile)
            for sampleName in jsonSample.keys():
                if 'TT_TuneCUETP8M1_13TeV-powheg-pythia8_Fall15MiniAODv2' in sampleName : 

                    ttflname = sampleName.replace("TT_Tune", "TT_FL_Tune")
                    jsonSample[ttflname] = copy.deepcopy(jsonSample[sampleName])
                    jsonSample[ttflname]["sample_cut"] = "(hh_gen_ttbar_decay_type >= 4 && hh_gen_ttbar_decay_type <= 10 && hh_gen_ttbar_decay_type != 7)"
                    jsonSample[ttflname]["output_name"] = jsonSample[sampleName]["output_name"].replace("TT_Tune", "TT_FL_Tune")

                    ttslname = sampleName.replace("TT_Tune", "TT_SL_Tune")
                    jsonSample[ttslname] = copy.deepcopy(jsonSample[sampleName])
                    jsonSample[ttslname]["sample_cut"] = "(hh_gen_ttbar_decay_type == 2 || hh_gen_ttbar_decay_type == 3 || hh_gen_ttbar_decay_type == 7)"
                    jsonSample[ttslname]["output_name"] = jsonSample[sampleName]["output_name"].replace("TT_Tune", "TT_SL_Tune")

                    ttfhname = sampleName.replace("TT_Tune", "TT_FH_Tune")
                    jsonSample[ttfhname] = copy.deepcopy(jsonSample[sampleName])
                    jsonSample[ttfhname]["sample_cut"] = "(hh_gen_ttbar_decay_type == 1)"
                    jsonSample[ttfhname]["output_name"] = jsonSample[sampleName]["output_name"].replace("TT_Tune", "TT_FH_Tune")
                    
                    jsonSample.pop(sampleName)
                
                if 'DYJetsToLL_M-5to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' in sampleName or 'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' in sampleName : 
                #if 'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX_MiniAODv2' in sampleName or 'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX_MiniAODv2' in sampleName : 
                    jsonSample[sampleName]["sample_cut"] = "event_ht < 100"

                # Handle the cluster v1tov3 reweighting
                if "all_nodes" in sampleName:
                    for node in range(1, 13):
                        node_str = "node_" + str(node)
                        newName = sampleName.replace("all_nodes", node_str)
                        jsonSample[newName] = copy.deepcopy(jsonSample[sampleName])
                        jsonSample[newName]["sample-weight"] = "cluster_" + node_str
                        jsonSample[newName]["output_name"] = jsonSample[sampleName]["output_name"].replace("all_nodes", node_str)
                    jsonSample.pop(sampleName)

        with open(jsonSampleFilePath, 'w+') as jsonSampleFile :
            json.dump(jsonSample, jsonSampleFile)
                

## Actually submit the jobs
## It is recommended to do a dry-run first without submitting to condor
if args.submit : 
    mySub.submitOnCondor()


## Example Json skeleton: the field "#DB_NAME#" will be filled by condorSubmitter.
## You can specify anything else you want that will be passed to createHistoWithtMultiDraw
## for this particular sample.
#{
#    "#DB_NAME#": {
#        "tree_name": "t",
#        "sample_cut": "1.",
#        # Optional:
#        # A job ID will be appended at the end of the name.
#        # If you have multiple runs, be sure to be change the name for each run in your python plot config.
#        "output_name": "output.root"
#    }
#}
