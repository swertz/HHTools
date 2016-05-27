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

#POSTMORIOND
#IDs.extend([1507, 1508, 1509, 1510, 1511, 1512, 1513, 1514, 1515, 1516, 1517, 1518, 1519, 1520, 1521, 1522, 1523, 1524, 1525, 1526, 1527, 1528, 1529, 1530, 1531, 1532, 1533, 1534, 1535, 1536, 1537, 1538, 1539, 1540, 1541, 1542, 1543, 1544, 1545, 1546, 1547, 1548, 1549, 1550, 1551, 1552, 1553, 1554, 1555, 1556, 1557, 1558, 1559, 1560, 1561, 1562, 1563, 1564, 1566, 1567, 1568, 1569, 1570, 1571, 1572, 1573, 1574, 1575, 1576, 1577, 1578, 1579, 1580, 1581, 1582, 1583, 1584, 1585, 1586, 1587, 1588, 1589, 1590, 1591, 1592, 1593, 1594, 1595, 1596, 1597, 1598, 1599, 1600, 1601, 1602, 1603, 1604, 1605, 1606, 1607, 1608, 1609, 1610])
#IDsToSplitMore.extend([1507, 1511, 1512, 1514, 1516, 1520, 1522, 1523, 1524, 1525, 1526, 1528, 1529, 1531, 1532, 1533, 1534, 1537, 1542, 1546, 1556, 1558, 1564, 1568, 1569, 1570, 1571, 1572, 1573, 1574, 1575, 1576, 1577, 1578, 1580, 1581, 1587, 1588, 1598, 1601, 1604])

# ICHEPv0

# All backgrounds and signals:
#IDs.extend([1614, 1615, 1616, 1617, 1618, 1619, 1620, 1621, 1622, 1623, 1624, 1625, 1626, 1627, 1628, 1629, 1630, 1631, 1632, 1633, 1634, 1635, 1636, 1637, 1638, 1639, 1640, 1641, 1642, 1643, 1644, 1645, 1646, 1647, 1648, 1649, 1650, 1651, 1652, 1653, 1654, 1655, 1656, 1657, 1658, 1659, 1660, 1661, 1662, 1663, 1664, 1665, 1666, 1667, 1668, 1669, 1670, 1671, 1672, 1673, 1674, 1675, 1676, 1677, 1678, 1679, 1680, 1681, 1682, 1683, 1684, 1685, 1686, 1687, 1688, 1689, 1690, 1691, 1692, 1693, 1694, 1695, 1696, 1697, 1698, 1699, 1700, 1701, 1702, 1703, 1704, 1705, 1706, 1707, 1708, 1709, 1710, 1711, 1712, 1713, 1714, 1715, 1716, 1717, 1718, 1719, 1720, 1721, 1722, 1723, 1724, 1725, 1726, 1727, 1728, 1729, 1730, 1731, 1732, 1733, 1734, 1735, 1736, 1737, 1738, 1739])

# Main backgrounds:
#IDs.extend([
#    1658, # tW 
#    1666, # tW
#    1715, # sT t-chan
#    1718, # TT incl NLO
#    #1733, # DY M10-50 NLO merged
#    #1734, # DY M-50 NLO merged 
#    ])
#
## DY LO
#IDs.extend([
#    # M-50 incl. merged
#    1739,
#    # M-50, binned HT > 100
#    1731,
#    1679,
#    1736,
#    1737,
#    # M-5to50 incl.
#    1717,
#    # M-5to50, binned HT
#    1738,
#    1705,
#    1680,
#    1735,
#    ])
IDs.extend([1737])

# Resonant
#IDs.extend([1617, 1625, 1630, 1631, 1638, 1640, 1647, 1652, 1654, 1660, 1665, 1668, 1669, 1674, 1676, 1678, 1685, 1686, 1689, 1695, 1699, 1700, 1704, 1706, 1708, 1728])

# NonResonant
IDs.extend([1614, 1618, 1626, 1634, 1635, 1639, 1651, 1672, 1673, 1677, 1684, 1697, 1698, 1722])

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

sample = get_sample(IDs[0])
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
    filesperJob = 10
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
            for sampleName in  jsonSample.keys():
#                if 'TT_TuneCUETP8M1_13TeV-powheg-pythia8_MiniAODv2' in sampleName : 
#
#                    ttflname = sampleName.replace("TT_Tune", "TT_FL_Tune")
#                    jsonSample[ttflname] = copy.deepcopy(jsonSample[sampleName])
#                    jsonSample[ttflname]["sample_cut"] = "(hh_gen_ttbar_decay_type >= 4 && hh_gen_ttbar_decay_type <= 10 && hh_gen_ttbar_decay_type != 7)"
#                    jsonSample[ttflname]["output_name"] = jsonSample[sampleName]["output_name"].replace("TT_Tune", "TT_FL_Tune")
#
#                    ttslname = sampleName.replace("TT_Tune", "TT_SL_Tune")
#                    jsonSample[ttslname] = copy.deepcopy(jsonSample[sampleName])
#                    jsonSample[ttslname]["sample_cut"] = "(hh_gen_ttbar_decay_type == 2 || hh_gen_ttbar_decay_type == 3 || hh_gen_ttbar_decay_type == 7)"
#                    jsonSample[ttslname]["output_name"] = jsonSample[sampleName]["output_name"].replace("TT_Tune", "TT_SL_Tune")
#
#                    ttfhname = sampleName.replace("TT_Tune", "TT_FH_Tune")
#                    jsonSample[ttfhname] = copy.deepcopy(jsonSample[sampleName])
#                    jsonSample[ttfhname]["sample_cut"] = "(hh_gen_ttbar_decay_type == 1)"
#                    jsonSample[ttfhname]["output_name"] = jsonSample[sampleName]["output_name"].replace("TT_Tune", "TT_FH_Tune")
#                    jsonSample.pop(sampleName)
                if 'DYJetsToLL_M-5to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' in sampleName or 'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' in sampleName : 
                #if 'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX_MiniAODv2' in sampleName or 'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX_MiniAODv2' in sampleName : 
                    jsonSample[sampleName]["sample_cut"] = "event_ht < 100"

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
