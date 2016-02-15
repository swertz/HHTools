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

#For pre approval : 
IDs = [1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1129, 1130, 1131, 1132, 1133, 1134, 1135, 1136, 1137, 1138, 1139, 1140, 1141, 1142, 1143, 1144, 1145, 1146, 1147, 1148, 1149, 1150, 1151, 1152, 1153, 1154, 1155, 1156, 1157, 1158, 1159, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167, 1168, 1169, 1170, 1171, 1172, 1173, 1174, 1175, 1176]
IDsToSplitMore =  []
#IDs = [1096, 1097, 1143] # signal and TT (last)
#IDs = [1174, 1156] # DY
#IDsToSplitMore =  []

parser = argparse.ArgumentParser(description='Facility to submit histFactory jobs on condor.')
parser.add_argument('-o', '--output', dest='output', default=str(datetime.date.today()), help='Name of the output directory.')
parser.add_argument('-s', '--submit', help='Choice to actually submit the jobs or not.', action="store_true")
parser.add_argument('-f', '--filter', dest='filter', default=False, help='Apply filter on DY ht and TT lepton flavour.', action="store_true")
parser.add_argument('-t', '--test', help='Run on the output of HHAnalyzer not yet in the DB.', action="store_true")
parser.add_argument('-p', '--plotter', dest='plotter', default="generatePlots.py", help='Code generating the plots.')
parser.add_argument('-r', '--remove', help='Overwrite output directory if it already exists.', action="store_true")

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
    filesperJob = 2 
    if ID in IDsToSplitMore :
        filesperJob = 1
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
                if 'TT_TuneCUETP8M1_13TeV-powheg-pythia8_MiniAODv2' in sampleName : 

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
