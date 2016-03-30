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
#For pre approval : 
#IDs = [1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1129, 1130, 1131, 1132, 1133, 1134, 1135, 1136, 1137, 1138, 1139, 1140, 1141, 1142, 1143, 1144, 1145, 1146, 1147, 1148, 1149, 1150, 1151, 1152, 1153, 1154, 1155, 1156, 1157, 1158, 1159, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167, 1168, 1169, 1170, 1171, 1172, 1173, 1174, 1175, 1176]
#FullIDs = [1205, 1206, 1207, 1208, 1209, 1210, 1211, 1212, 1213, 1214, 1215, 1216, 1217, 1218, 1219, 1220, 1221, 1222, 1223, 1224, 1225, 1226, 1227, 1228, 1229, 1230, 1231, 1232, 1233, 1234, 1235, 1236, 1237, 1238, 1239, 1240, 1241, 1242, 1243, 1244, 1245, 1246, 1247, 1248, 1249, 1250, 1251, 1252, 1253, 1254, 1255, 1256, 1257, 1258, 1259, 1260, 1261, 1262, 1263, 1264, 1265, 1266, 1267, 1268, 1269, 1270, 1271, 1272, 1273, 1274, 1275, 1276, 1277, 1282, 1283, 1289, 1293, 1294, 1300, 1302, 1303, 1306, 1307, 1308, 1309, 1310, 1311, 1312, 1313, 1314, 1315, 1316, 1317, 1318, 1319, 1320, 1321, 1322, 1323, 1324]
#IDs = [1206, 1208, 1210, 1211, 1216, 1217, 1218, 1223, 1226, 1230, 1232, 1234, 1235, 1236, 1237, 1238, 1239, 1241, 1243, 1244, 1247, 1248, 1250, 1251, 1253, 1255, 1257, 1259, 1261, 1262, 1263, 1264, 1265, 1266, 1267, 1270, 1273, 1274, 1275, 1276, 1277, 1293, 1294, 1300, 1303, 1306, 1307, 1308, 1309, 1310, 1311, 1312, 1313, 1314, 1315, 1316, 1317, 1318, 1319, 1320, 1321, 1324]
#LAST prod for ARC review
IDs.extend([1330, 1333, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1341, 1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351, 1352, 1353, 1354, 1355, 1356, 1357, 1358, 1359, 1360, 1361, 1362, 1363, 1364, 1365, 1366, 1367, 1368, 1369, 1370, 1371, 1372, 1373, 1374, 1375, 1377, 1378, 1379, 1380, 1381, 1382, 1390, 1391, 1393, 1396, 1403, 1404, 1417, 1420, 1421, 1422, 1423, 1424, 1425, 1426, 1427, 1428, 1429, 1430, 1431, 1435, 1438, 1376, 1433, 1436, 1444, 1445, 1446, 1453]) 
IDs.remove(1347) # Old Radion 450 which changed name it is now 1453
#Data : 1376, 1433, 1436, 1444, 1445, 1446
# TT mcatnlo : 1443 
IDs.extend(range(1454, 1462)) # missing VV
IDs.remove(1458) # ZZTo2L2Nu scale systematic buggy
IDs.extend([1448, 1449, 1450, 1451]) #TTV forgotten in runPostCrab
IDsToSplitMore = [1333, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1341, 1346, 1347, 1348, 1349, 1350, 1351, 1352, 1353, 1354, 1360, 1361, 1370, 1371, 1396, 1403, 1404, 1417, 1438, 1453] 
IDsToSplitLitleMore = [1359, 1426]
#IDs = [1253, 1308] #DY inclusive M5-50 --> 1253, M > 50 --> 1308
#IDs.extend([ # DY pthat bins 5-50
#    1220,
#    1228,
#    1231,
#    1252,
#])
#IDs.extend([ # DY pthat bins 50
#    1249,
#    1271,
#    1272,
#])
#IDs.append(1277) # TTFL
#IDsToSplitMore =  [1237, 1238, 1239, 1243, 1267, 1275]
#IDs = [1096, 1097, 1143] # signal and TT (last)
#IDs = [1174, 1156] # DY
#IDsToSplitMore =  []

# ARC ANSWER 
#IDs.extend([1247,   # 2015 D data from previous prod
#    1265,
#    1273,
#    1274,
#    1307,
#    1312])
#

parser = argparse.ArgumentParser(description='Facility to submit histFactory jobs on condor.')
parser.add_argument('-o', '--output', dest='output', default=str(datetime.date.today()), help='Name of the output directory.')
parser.add_argument('-s', '--submit', help='Choice to actually submit the jobs or not.', action="store_true")
parser.add_argument('-f', '--filter', dest='filter', default=True, help='Apply filter on DY ht.')
parser.add_argument('-t', '--test', help='Run on the output of HHAnalyzer not yet in the DB.', action="store_true")
parser.add_argument('-p', '--plotter', dest='plotter', default="generatePlots.py", help='Code generating the plots.')
parser.add_argument('-r', '--remove', help='Overwrite output directory if it already exists.', action="store_true")
parser.add_argument('--skip', help='Skip the building part.', action="store_true")

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
    filesperJob = 5  
    if ID in IDsToSplitMore :
        filesperJob = 1
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

#print rootFileName
if not args.skip :
    if args.test : 
        os.system("../../CommonTools/histFactory/build/createPlotter.sh %s %s %s"%(rootFileName, args.plotter, args.output))
    else : 
        os.system("../../CommonTools/histFactory/build/createPlotter.sh %s %s %s"%(files[0], args.plotter, args.output))

mySub = condorSubmitter(samples, "%s/build/plotter.exe"%args.output, "DUMMY", args.output+"/", rescale = True)

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
