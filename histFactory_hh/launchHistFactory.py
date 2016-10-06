#!/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/bin/python

# usage dans histfactory_hh : python launchHistFactory.py outputName [submit]

import sys, os, json
import copy
import datetime

import argparse

from cp3_llbb.CommonTools.condorTools import condorSubmitter

# Add default ingrid storm package
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/storm-0.20-py2.7-linux-x86_64.egg')
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/MySQL_python-1.2.3-py2.7-linux-x86_64.egg')

CMSSW_BASE = os.environ['CMSSW_BASE']
SCRAM_ARCH = os.environ['SCRAM_ARCH']
sys.path.append(os.path.join(CMSSW_BASE, 'bin', SCRAM_ARCH))
from SAMADhi import Dataset, Sample, DbStore

def build_sample_name(name, tag):
    return "{}*{}".format(name, tag)

# Connect to the database
dbstore = DbStore()

def get_sample_ids_from_name(name):
    results = dbstore.find(Sample, Sample.name.like(unicode(name.replace('*', '%'))))

    if results.count() == 0:
        return None

    if results.count() > 1:
        print("Note: more than one sample found in the database matching %r. This is maybe not what you expected:" % name)
        for sample in results:
            print("    %s" % sample.name)

    ids = []
    for sample in results:
        ids.append(sample.sample_id)

    return ids

def get_sample(iSample):
    resultset = dbstore.find(Sample, Sample.sample_id == iSample)
    return resultset.one()

# Warning: put most recent tags first!
analysis_tags = [
        'v0.1.4+76X_HHAnalysis_2016-06-03.v0',
        'v0.1.2+76X_HHAnalysis_2016-05-02.v0'
        ]

Samples = []
SamplesToSplitMore = []

# Data
Samples.extend([
    'DoubleEG', # DoubleEG
    'MuonEG', # MuonEG
    'DoubleMuon', # DoubleMuon
    ])

# Main backgrounds:
Samples.extend([
    'ST_tW_top_5f_inclusiveDecays_13TeV-powheg', # tW top
    'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg', # tW atop
    'ST_t-channel_4f_leptonDecays_13TeV-amcatnlo', # sT t-chan
    'TT_TuneCUETP8M1_13TeV-powheg-pythia8', # TT incl NLO
    'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_extended', # DY M10-50 NLO merged
    'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_extended', # DY M-50 NLO merged 
    ])

# DY LO
Samples.extend([
    # M-50 incl. merged
    'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended',
    # M-50, binned HT > 100
    'DYJetsToLL_M-50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 100-200 non-merged
    'DYJetsToLL_M-50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 200-400 non-merged
    'DYJetsToLL_M-50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended', # 400-600 merged
    'DYJetsToLL_M-50_HT-600toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended', # 600-Inf merged
    # M-5to50 incl.: forget it...
    'DYJetsToLL_M-5to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
    # M-5to50, binned HT
    'DYJetsToLL_M-5to50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended', # 100-200 merged
    'DYJetsToLL_M-5to50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 200-400 non-merged
    'DYJetsToLL_M-5to50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 400-600 non-merged
    'DYJetsToLL_M-5to50_HT-600toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended', # 600-Inf merged
    ])
#
# Other backgrounds
# VV
Samples.extend([
    #'VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8', # VV(2L2Nu)
    
    'WWToLNuQQ_13TeV-powheg', # WW(LNuQQ)
    'WWTo2L2Nu_13TeV-powheg', # WW(2L2Nu)
    
    'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8', # WZ(3LNu)
    'WZTo1L3Nu_13TeV_amcatnloFXFX_madspin_pythia8', # WZ(L3Nu)
    'WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8', # WZ(LNu2Q)
    'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8', # WZ(2L2Q)
    
    'ZZTo4L_13TeV_powheg_pythia8', # ZZ(4L)
    'ZZTo2L2Nu_13TeV_powheg_pythia8', # ZZ(2L2Nu)
    'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8', # ZZ(2L2Q)
    
    'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8', # WZZ
    ])

# Higgs
Samples.extend([
    # ggH ==> no H(ZZ)?
    'GluGluHToWWTo2L2Nu_M125_13TeV_powheg_JHUgen_pythia8', # H(WW(2L2Nu))
    'GluGluHToBB_M125_13TeV_powheg_pythia8', # H(BB)

    # ZH
    'GluGluZH_HToWWTo2L2Nu_ZTo2L_M125_13TeV_powheg_pythia8', # ggZ(LL)H(WW(2L2Nu))
    'HZJ_HToWW_M125_13TeV_powheg_pythia8', # ZH(WW)
    'ggZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8', # ggZ(LL)H(BB)
    'ZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8', # Z(LL)H(BB)
    'ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8', # ggZ(NuNu)H(BB)
    
    # VBF
    'VBFHToBB_M-125_13TeV_powheg_pythia8', # VBFH(BB)
    'VBFHToWWTo2L2Nu_M125_13TeV_powheg_JHUgen_pythia8', # VBFH(WW(2L2Nu))

    # WH
    'WplusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8', # W+(LNu)H(BB)
    'WminusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8', # W-(LNu)H(BB)
    'HWplusJ_HToWW_M125_13TeV_powheg_pythia8', # W+H(WW)
    'HWminusJ_HToWW_M125_13TeV_powheg_pythia8', # W-H(WW)

    # bbH
    'bbHToBB_M-125_4FS_ybyt_13TeV_amcatnlo', # bbH(BB) ybyt
    'bbHToBB_M-125_4FS_yb2_13TeV_amcatnlo', # bbH(BB) yb2
    'bbHToWWTo2L2Nu_M-125_4FS_ybyt_13TeV_amcatnlo', # bbH(WW) ybyt
    'bbHToWWTo2L2Nu_M-125_4FS_yb2_13TeV_amcatnlo', # bbH(WW) yb2
    ])

# Top
Samples.extend([
    'ST_s-channel_4f_leptonDecays_13TeV-amcatnlo', # sT s-channel
    'TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8', # TTW(LNu)
    'TTWJetsToQQ_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8', # TTW(QQ)
    'TTZToLLNuNu_M-10_TuneCUETP8M1_13TeV-amcatnlo-pythia8', # TTZ(2L2Nu)
    'TTZToQQ_TuneCUETP8M1_13TeV-amcatnlo-pythia8', # TTZ(QQ),
    'ttHTobb_M125_13TeV_powheg_pythia8', # ttH(bb)
    'ttHToNonbb_M125_13TeV_powheg_pythia8', # ttH(nonbb)
    # 'TTTo2L2Nu_13TeV-powheg', # TT(2L2Nu)
    ])

# # TT aMC@NLO
# Samples.append('TTJets_TuneCUETP8M1_amcatnloFXFX')

# Wjets
Samples.extend([
    'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', # JetsLNu

    # HT binned
    'WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 200-400
    'WJetsToLNu_HT-800To1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 800-1200
    'WJetsToLNu_HT-1200To2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 1200 - 2500
    'WJetsToLNu_HT-2500ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 2500 - Inf 
    ])

# QCD ==> 30to50 missing
# Samples.extend([
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
SamplesToSplitMore.extend([
    'GluGluToHHTo2B2VTo2L2Nu_node_SM_13TeV-madgraph', # SM
    'GluGluToHHTo2B2VTo2L2Nu_node_box_13TeV-madgraph', # box
    ])

# NonResonant merged
SamplesToSplitMore.append('GluGluToHHTo2B2VTo2L2Nu_all_nodes_13TeV-madgraph')

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

# Convert samples into ids
def convert_to_ids(samples):
    ids = []
    for sample in samples:
        found = False
        for tag in analysis_tags:
            ids_ = get_sample_ids_from_name(build_sample_name(sample, tag))
            if ids_:
                found = True
                ids.extend(ids_)
                break

        if not found:
            raise Exception("No sample found in the database for %r" % sample)

    return ids

IDs = convert_to_ids(Samples)
IDsToSplitMore = convert_to_ids(SamplesToSplitMore)

# Find first MC sample and use one file as skeleton
for id in IDs:
    sample = get_sample(id)
    if sample.source_dataset.datatype != "mc":
        continue

    skeleton_file = "/storage/data/cms/" + sample.files.any().lfn
    print("Using %r as skeleton" % skeleton_file)
    break

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

toolDir = "Factories"

toolScript = "createPlotter.sh"
executable = "plotter.exe"
if args.treeFactory: 
    executable = "skimmer.exe"
    toolScript = "createSkimmer.sh"

if not args.skip :
    if args.test : 
        os.system(os.path.join("../../", "CommonTools", "Factories", "build", toolScript) + " %s %s %s"%(rootFileName, args.plotter, args.output))
    else : 
        os.system(os.path.join("../../", "CommonTools", "Factories", "build", toolScript) + " %s %s %s"%(files[0], args.plotter, args.output))

## Create Condor submitter to handle job creating
mySub = condorSubmitter(samples, "%s/build/" % args.output + executable, "DUMMY", args.output+"/", rescale = True)

## Create test_condor directory and subdirs
mySub.setupCondorDirs()

splitTT = False
splitDY = False

operators_MV = ["OtG", "Otphi", "O6", "OH"]
rwgt_base = [ "SM", "box" ] + range(2, 13)

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

        if splitDY and 'DYJetsToLL_' in sample["db_name"]:

            # Z + jj' ; j = b/c, j' = b/c
            dy_bb_sample = copy.deepcopy(sample)
            newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])

            dy_bb_sample["db_name"] = sample["db_name"].replace("DYJetsToLL", "DYBBOrCCOrBCToLL")
            newJson["sample_cut"] = "(hh_llmetjj_HWWleptons_nobtag_csv.gen_bb || hh_llmetjj_HWWleptons_nobtag_csv.gen_cc || hh_llmetjj_HWWleptons_nobtag_csv.gen_bc)"

            dy_bb_sample["json_skeleton"][dy_bb_sample["db_name"]] = newJson
            dy_bb_sample["json_skeleton"].pop(sample["db_name"])
            mySub.sampleCfg.append(dy_bb_sample)

            # Z + jj' ; j = b/c, j' = l
            dy_bx_sample = copy.deepcopy(sample)
            newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])

            dy_bx_sample["db_name"] = sample["db_name"].replace("DYJetsToLL", "DYBXOrCXToLL")
            newJson["sample_cut"] = "(hh_llmetjj_HWWleptons_nobtag_csv.gen_bl || hh_llmetjj_HWWleptons_nobtag_csv.gen_cl)"

            dy_bx_sample["json_skeleton"][dy_bx_sample["db_name"]] = newJson
            dy_bx_sample["json_skeleton"].pop(sample["db_name"])
            mySub.sampleCfg.append(dy_bx_sample)

            # Z + jj' ; j = l, j' = l
            dy_xx_sample = copy.deepcopy(sample)
            newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])

            dy_xx_sample["db_name"] = sample["db_name"].replace("DYJetsToLL", "DYXXToLL")
            newJson["sample_cut"] = "(hh_llmetjj_HWWleptons_nobtag_csv.gen_ll)"

            dy_xx_sample["json_skeleton"][dy_xx_sample["db_name"]] = newJson
            dy_xx_sample["json_skeleton"].pop(sample["db_name"])
            mySub.sampleCfg.append(dy_xx_sample)

        # Merging with HT binned sample: add cut on inclusive one
        if 'DYJetsToLL_M-5to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' in sample["db_name"] or 'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' in sample["db_name"]: 
            sample["json_skeleton"][sample["db_name"]]["sample_cut"] = "event_ht < 100"

        if 'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8' in sample["db_name"]:
            sample["json_skeleton"][sample["db_name"]]["sample_cut"] = "event_ht < 100"

        ## Cluster to 1507 points reweighting (template-based)
        #if "all_nodes" in sample["db_name"]:
        #    ## For v1->v1 reweighting check:
        #    #for node in range(2, 14):
        #    #    node_str = "node_rwgt_" + str(node)
        #    #for node in range(1, 13):

        #    #    newSample = copy.deepcopy(sample)
        #    #    newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])
        #    #    
        #    #    node_str = "node_" + str(node)
        #    #    newSample["db_name"] = sample["db_name"].replace("all_nodes", node_str)
        #    #    newJson["sample-weight"] = "cluster_" + node_str
        #    #    
        #    #    newSample["json_skeleton"][newSample["db_name"]] = newJson
        #    #    newSample["json_skeleton"].pop(sample["db_name"])
        #    #    mySub.sampleCfg.append(newSample)
        #    
        #    # 1507 points
        #    for node in range(0, 1507):
        #        # Skip dummy Xanda
        #        if node in [324, 910, 985, 990]: continue

        #        newSample = copy.deepcopy(sample)
        #        newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])
        #        
        #        node_str = "point_" + str(node)
        #        newSample["db_name"] = sample["db_name"].replace("all_nodes", node_str)
        #        newJson["sample-weight"] = node_str
        #        
        #        newSample["json_skeleton"][newSample["db_name"]] = newJson
        #        newSample["json_skeleton"].pop(sample["db_name"])
        #        mySub.sampleCfg.append(newSample)

        #    mySub.sampleCfg.remove(sample)

        ## Cluster to MV reweighting (ME-based)
        #if "node" in sample["db_name"]:
        #    for base, base_name in enumerate(rwgt_base):
        #        for i, op1 in enumerate(operators_MV):
        #            newSample = copy.deepcopy(sample)
        #            newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])
        #            
        #            newSample["db_name"] = sample["db_name"].replace("node_" + base_name, "SM_" + op1)
        #            newJson["sample-weight"] = "base_" + base_name + "_SM_" + op1
        #            
        #            newSample["json_skeleton"][newSample["db_name"]] = newJson
        #            newSample["json_skeleton"].pop(sample["db_name"])
        #            
        #            mySub.sampleCfg.append(newSample)
        #
        #            for j, op2 in enumerate(operators_MV):
        #                if i < j: continue
        #            
        #                newSample = copy.deepcopy(sample)
        #                newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])
        #                
        #                newSample["db_name"] = sample["db_name"].replace("node_" + base_name, op1 + "_" + op2)
        #                newJson["sample-weight"] = "base_" + base_name + "_" + op1 + "_" + op2
        #                
        #                newSample["json_skeleton"][newSample["db_name"]] = newJson
        #                newSample["json_skeleton"].pop(sample["db_name"])
        #                
        #                mySub.sampleCfg.append(newSample)

## Write command and data files in the condor directory
mySub.createCondorFiles()

# Actually submit the jobs
# It is recommended to do a dry-run first without submitting to condor
if args.submit: 
   mySub.submitOnCondor()
