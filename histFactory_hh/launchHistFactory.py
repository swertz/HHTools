#! /bin/env python

import sys, os, json
import copy
import datetime
import subprocess

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
        'v4.1.0+80X_HHAnalysis_2016-12-14.v0'
        ]

parser = argparse.ArgumentParser(description='Facility to submit histFactory jobs on condor.')
parser.add_argument('-o', '--output', dest='output', default=str(datetime.date.today()), help='Name of the output directory.')
parser.add_argument('-s', '--submit', help='Choice to actually submit the jobs or not.', action="store_true")
parser.add_argument('-f', '--filter', dest='filter', default=True, help='Apply filter on DY ht.')
parser.add_argument('-t', '--test', help='Run on the output of HHAnalyzer not yet in the DB.', action="store_true")
parser.add_argument('-r', '--remove', help='Overwrite output directory if it already exists.', action="store_true")
parser.add_argument('--skip', help='Skip the building part.', action="store_true")
parser.add_argument('--tree', dest='treeFactory', action='store_true', default=False, help='Use treeFactory instead of histFactory')

args = parser.parse_args()

def get_configuration_file(placeholder):
    return placeholder.format("Trees" if args.treeFactory else "Plots")

def get_sample_splitting(sample):
    return 10

class Configuration:
    def __init__(self, config, suffix=''):
        self.samples = []
        self.sample_ids = []
        self.configuration_file = config
        self.suffix = suffix

    def get_sample_ids(self):
        for sample in self.samples:
            found = False
            for tag in analysis_tags:
                ids_ = get_sample_ids_from_name(build_sample_name(sample, tag))
                if ids_:
                    found = True
                    self.sample_ids.extend(ids_)
                    break

            if not found:
                raise Exception("No sample found in the database for %r" % sample)

MainConfiguration = Configuration(get_configuration_file('generate{}.py'))
DYOnlyConfiguration = Configuration(get_configuration_file('generate{}ForDY.py'), suffix='_for_dy')

# Data
MainConfiguration.samples.extend([
    'DoubleEG', # DoubleEG
    'MuonEG', # MuonEG
    'DoubleMuon', # DoubleMuon
    ])

# Main backgrounds:
MainConfiguration.samples.extend([
    'ST_tW_top_5f_inclusiveDecays_13TeV-powheg', # tW top
    'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg', # tW atop
    'ST_t-channel_4f_leptonDecays_13TeV-amcatnlo', # sT t-chan
    # 'TT_TuneCUETP8M1_13TeV-powheg-pythia8_ext4', # TT incl NLO
    'TTTo2L2Nu_13TeV-powheg_ext1', # TT -> 2L 2Nu NLO
    ])

# # DY NLO (included with other backgrounds)
MainConfiguration.samples.extend([
  'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', # DY M10-50 NLO merged
  'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', # DY M-50 NLO merged
])

# DY LO
MainConfiguration.samples.extend([
    # M-50 incl. merged
    # 'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended',
    # M-50, binned HT > 100
    # 'DYJetsToLL_M-50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 100-200 non-merged
    # 'DYJetsToLL_M-50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 200-400 non-merged
    # 'DYJetsToLL_M-50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended', # 400-600 merged
    # 'DYJetsToLL_M-50_HT-600toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended', # 600-Inf merged
    # M-5to50 incl.: forget it...
    # 'DYJetsToLL_M-5to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
    # M-5to50, binned HT
    # 'DYJetsToLL_M-5to50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended', # 100-200 merged
    # 'DYJetsToLL_M-5to50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 200-400 non-merged
    # 'DYJetsToLL_M-5to50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 400-600 non-merged
    # 'DYJetsToLL_M-5to50_HT-600toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended', # 600-Inf merged
    ])

#
# Other backgrounds
# VV
MainConfiguration.samples.extend([
    #'VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8', # VV(2L2Nu)

    # 'WWToLNuQQ_13TeV-powheg', # WW(LNuQQ)
    # 'WWTo2L2Nu_13TeV-powheg', # WW(2L2Nu)

    # 'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8', # WZ(3LNu)
    # 'WZTo1L3Nu_13TeV_amcatnloFXFX_madspin_pythia8', # WZ(L3Nu)
    # 'WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8', # WZ(LNu2Q)
    # 'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8', # WZ(2L2Q)

    # 'ZZTo4L_13TeV_powheg_pythia8', # ZZ(4L)
    # 'ZZTo2L2Nu_13TeV_powheg_pythia8', # ZZ(2L2Nu)
    # 'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8', # ZZ(2L2Q)

    # 'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8', # WZZ
    ])

# Higgs
MainConfiguration.samples.extend([
    # # ggH ==> no H(ZZ)?
    # 'GluGluHToWWTo2L2Nu_M125_13TeV_powheg_JHUgen_pythia8', # H(WW(2L2Nu))
    # 'GluGluHToBB_M125_13TeV_powheg_pythia8', # H(BB)

    # # ZH
    # 'GluGluZH_HToWWTo2L2Nu_ZTo2L_M125_13TeV_powheg_pythia8', # ggZ(LL)H(WW(2L2Nu))
    # 'HZJ_HToWW_M125_13TeV_powheg_pythia8', # ZH(WW)
    # 'ggZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8', # ggZ(LL)H(BB)
    # 'ZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8', # Z(LL)H(BB)
    # 'ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8', # ggZ(NuNu)H(BB)

    # # VBF
    # 'VBFHToBB_M-125_13TeV_powheg_pythia8', # VBFH(BB)
    # 'VBFHToWWTo2L2Nu_M125_13TeV_powheg_JHUgen_pythia8', # VBFH(WW(2L2Nu))

    # # WH
    # 'WplusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8', # W+(LNu)H(BB)
    # 'WminusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8', # W-(LNu)H(BB)
    # 'HWplusJ_HToWW_M125_13TeV_powheg_pythia8', # W+H(WW)
    # 'HWminusJ_HToWW_M125_13TeV_powheg_pythia8', # W-H(WW)

    # # bbH
    # 'bbHToBB_M-125_4FS_ybyt_13TeV_amcatnlo', # bbH(BB) ybyt
    # 'bbHToBB_M-125_4FS_yb2_13TeV_amcatnlo', # bbH(BB) yb2
    # 'bbHToWWTo2L2Nu_M-125_4FS_ybyt_13TeV_amcatnlo', # bbH(WW) ybyt
    # 'bbHToWWTo2L2Nu_M-125_4FS_yb2_13TeV_amcatnlo', # bbH(WW) yb2
    ])

# Top
MainConfiguration.samples.extend([
    # 'ST_s-channel_4f_leptonDecays_13TeV-amcatnlo', # sT s-channel
    # 'TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8', # TTW(LNu)
    # 'TTWJetsToQQ_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8', # TTW(QQ)
    # 'TTZToLLNuNu_M-10_TuneCUETP8M1_13TeV-amcatnlo-pythia8', # TTZ(2L2Nu)
    # 'TTZToQQ_TuneCUETP8M1_13TeV-amcatnlo-pythia8', # TTZ(QQ),
    # 'ttHTobb_M125_13TeV_powheg_pythia8', # ttH(bb)
    # 'ttHToNonbb_M125_13TeV_powheg_pythia8', # ttH(nonbb)
    ])

# # TT aMC@NLO
# MainConfiguration.samples.append('TTJets_TuneCUETP8M1_amcatnloFXFX')

# Wjets
MainConfiguration.samples.extend([
    # 'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', # JetsLNu

    # # HT binned
    # 'WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 200-400
    # 'WJetsToLNu_HT-800To1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 800-1200
    # 'WJetsToLNu_HT-1200To2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 1200 - 2500
    # 'WJetsToLNu_HT-2500ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 2500 - Inf
    ])

# QCD ==> 30to50 missing
# MainConfiguration.samples.extend([
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
MainConfiguration.samples.extend([
    # 'GluGluToHHTo2B2VTo2L2Nu_node_SM_13TeV-madgraph', # SM
    # 'GluGluToHHTo2B2VTo2L2Nu_node_box_13TeV-madgraph', # box
    ])

# Resonant signal
MainConfiguration.samples.extend([
    'GluGluToRadionToHHTo2B2VTo2L2Nu_M'
])

# Non-resonant signal
MainConfiguration.samples.extend([
    'GluGluToHHTo2B2VTo2L2Nu_node_'
])

# NonResonant merged
# MainConfiguration.samples.append('GluGluToHHTo2B2VTo2L2Nu_all_nodes_13TeV-madgraph')

# DY NLO (separated from the rest because it's estimated from the data with help of the no-btag sample)
# Just comment if you don't want to process DY separately from the rest
DYOnlyConfiguration.samples = [
    'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', # DY M10-50 NLO merged
    'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', # DY M-50 NLO merged
]

#if not args.treeFactory:
#    # FIXME: We don't have currently a special configuration file for DY when doing plots
#    # For the moment, simply move samples into the main configuration
#    MainConfiguration.samples.extend(DYOnlyConfiguration.samples)
#    DYOnlyConfiguration.samples = []

#configurations = [ DYOnlyConfiguration ]
configurations = [ MainConfiguration ]

for c in configurations:
    c.get_sample_ids()

# Find first MC sample and use one file as skeleton
skeleton_file = None
for c in configurations:
    for id in c.sample_ids:
        sample = get_sample(id)
        if sample.source_dataset.datatype != "mc":
            continue

        skeleton_file = "/storage/data/cms/" + sample.files.any().lfn
        print("Using %r as skeleton" % skeleton_file)
        break

    if skeleton_file:
        break

if not skeleton_file:
    print("Warning: No MC file found in this job. Looking for data")

for c in configurations:
    for id in c.sample_ids:
        sample = get_sample(id)
        if sample.source_dataset.datatype != "data":
            continue

        skeleton_file = "/storage/data/cms/" + sample.files.any().lfn
        print("Using %r as skeleton" % skeleton_file)
        break

    if skeleton_file:
        break

if not skeleton_file:
    raise Exception("No file found in this job")

if args.test:
    jsonName = "jsonTest.json"
    jsonFile = open(jsonName)
    datasetDict = json.load(jsonFile)
    for datasetName in datasetDict.keys():
        rootFileName = datasetDict[datasetName]["files"][0]
        break

## Use treeFactory or histFactory

toolDir = "Factories"

toolScript = "createPlotter.sh"
executable = "plotter.exe"
configPath = '.'

if args.treeFactory:
    toolScript = "createSkimmer.sh"
    executable = "skimmer.exe"
    configPath = '../treeFactory_hh'

if not args.skip:
    def create_factory(config_file, output):
        print("")
        print("Generating factory in %r using %r" % (output, config_file))
        print("")

        if args.remove and os.path.isdir(output):
            print "Are you sure you want to execute the following command ?"
            print "rm -r " + output
            print "Type enter if yes, ctrl-c if not."
            raw_input()
            os.system("rm -r " + output)
            print "Deleted %r folder" % output
        cmd = [os.path.join("../../", "CommonTools", toolDir, "build", toolScript)]
        if args.test:
            cmd += [rootFileName]
        else:
            cmd += [skeleton_file]
        cmd += [config_file, output]

        # Raise exception if failing
        subprocess.check_call(cmd)
        print("Done")

    for c in configurations:
        if len(c.sample_ids) > 0:
            create_factory(os.path.join(configPath, c.configuration_file), args.output + c.suffix)

def create_condor(samples, output):
    ## Create Condor submitter to handle job creating
    mySub = condorSubmitter(samples, "%s/build/" % output + executable, "DUMMY", output + "/", rescale=True)

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

                dy_bb_sample["db_name"] = sample["db_name"].replace("DYJetsToLL", "DYBBOrCCToLL")
                newJson["sample_cut"] = "(hh_llmetjj_HWWleptons_nobtag_cmva.gen_bb || hh_llmetjj_HWWleptons_nobtag_cmva.gen_cc)"

                dy_bb_sample["json_skeleton"][dy_bb_sample["db_name"]] = newJson
                dy_bb_sample["json_skeleton"].pop(sample["db_name"])
                mySub.sampleCfg.append(dy_bb_sample)

                # Z + jj' ; j = b/c, j' = l
                dy_bx_sample = copy.deepcopy(sample)
                newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])

                dy_bx_sample["db_name"] = sample["db_name"].replace("DYJetsToLL", "DYBXOrCXToLL")
                newJson["sample_cut"] = "(hh_llmetjj_HWWleptons_nobtag_cmva.gen_bl || hh_llmetjj_HWWleptons_nobtag_cmva.gen_cl || hh_llmetjj_HWWleptons_nobtag_cmva.gen_bc)"

                dy_bx_sample["json_skeleton"][dy_bx_sample["db_name"]] = newJson
                dy_bx_sample["json_skeleton"].pop(sample["db_name"])
                mySub.sampleCfg.append(dy_bx_sample)

                # Z + jj' ; j = l, j' = l
                dy_xx_sample = copy.deepcopy(sample)
                newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])

                dy_xx_sample["db_name"] = sample["db_name"].replace("DYJetsToLL", "DYXXToLL")
                newJson["sample_cut"] = "(hh_llmetjj_HWWleptons_nobtag_cmva.gen_ll)"

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

for c in configurations:
    if len(c.sample_ids) == 0:
        continue

    condor_samples = []
    for id in c.sample_ids:
        condor_samples.append({'ID': id, 'files_per_job': get_sample_splitting(get_sample(id).name)})

    create_condor(condor_samples, args.output + c.suffix)
